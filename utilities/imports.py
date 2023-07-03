import base64
import io
import os
import shutil

import requests
import urllib3
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files import File
from PIL import Image

from brand.models import (
    Brand,
    BrandAsset,
    BrandCategory,
    BrandKeyPerson,
    BrandOnlineStore,
    BrandTag,
    BrandVisual,
    Person,
)
from brandscanner.settings.base import BASE_DIR
from utilities.converters import str_to_md5
from utilities.validators import is_none_or_empty_string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IMAGE_FILE_EXTENSIONS = ["jpg", "png", "webp", "svg"]
IMAGE_DOWNLOAD_DIR = f"{BASE_DIR}/tmp/prefill/img"
SUPPLIED_TAG = "SUPPLIED"


def _check_if_existing_brandasset(new_model: BrandAsset) -> bool:
    if new_model.asset is not None:
        filename = new_model.asset.file.name.split(".")[0]
        return BrandAsset.objects.filter(asset__icontains=filename).exists()
    return False


CHECK_IF_EXISTING = {"BrandAsset": _check_if_existing_brandasset}

IGNORE_MODEL_ON_ERROR = {
    "BrandAsset": {"asset": ["This field cannot be blank."]}
}


def _print_model(model_name, model_obj):
    print(f"\nFor model {model_name}, model fields are:")
    for field in model_obj._meta.get_fields():
        try:
            print("  ", field.name, ":", field.value_from_object(model_obj))
        except AttributeError:
            pass


def _model_adjusted_csv_src_value(
    model_field_rules, model_field_type, model_field_name, csv_src_value
):
    if is_none_or_empty_string(csv_src_value):
        default_value = model_field_rules[model_field_name].get(
            "default", None
        )
        if default_value is not None:
            csv_src_value = default_value
    else:
        csv_src_value = csv_src_value.strip()

        if model_field_type in ["enum"]:
            csv_src_value = model_field_rules[model_field_name]["choices"][
                csv_src_value
            ]

    return csv_src_value


def _download_image(image_url) -> bool:
    if is_none_or_empty_string(image_url):
        return False

    md5_name = str_to_md5(image_url)
    for ext in IMAGE_FILE_EXTENSIONS:
        if os.path.exists(f"{md5_name}.{ext}"):
            print("Image alredy exists. Skipping download.")
            return True

    jpg_b64_prefix = "data:image/jpeg;base64,"
    png_b64_prefix = "data:image/png;base64,"
    if image_url.startswith(jpg_b64_prefix):
        prefix_len = len(jpg_b64_prefix)
        image_b64 = image_url[prefix_len:]
        Image.open(io.BytesIO(base64.b64decode(image_b64))).save(
            f"{IMAGE_DOWNLOAD_DIR}/{md5_name}.jpg"
        )
    elif image_url.startswith(png_b64_prefix):
        prefix_len = len(png_b64_prefix)
        image_b64 = image_url[prefix_len:]
        Image.open(io.BytesIO(base64.b64decode(image_b64))).save(
            f"{IMAGE_DOWNLOAD_DIR}/{md5_name}.png"
        )
    else:
        # Remove all query params.
        # Assuming image url will end with image file ext.

        image_url = image_url.split("?")[0]
        image_ext = None

        if image_url.endswith(".jpg") or image_url.endswith(".jpeg"):
            image_ext = "jpg"
        if image_url.endswith(".png"):
            image_ext = "png"
        elif image_url.endswith(".webp"):
            image_ext = "webp"
        elif image_url.endswith(".svg"):
            image_ext = "svg"
        else:
            image_ext = "jpg"

        resp = requests.get(image_url, stream=True, verify=False)
        if resp.status_code != 200:
            del resp
            print("Non OK return code while downloading image.")
            return False

        with open(f"{IMAGE_DOWNLOAD_DIR}/{md5_name}.{image_ext}", "wb") as f:
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)

        del resp

    return True


def _run_pre_checks(model_name, model_rules, csv_row, foreign) -> bool:
    must = model_rules["pre"].get("must", [])
    model_field_rules = model_rules["fields"]

    for model_field_name in must:
        csv_src_col_name = model_field_rules[model_field_name].get(
            "source", f"{SUPPLIED_TAG}.{model_name}.{model_field_name}"
        )
        csv_src_value = csv_row.get(csv_src_col_name)

        if is_none_or_empty_string(csv_src_value):
            print(f"Value for field {model_field_name} not found.")
            return True

    accept = model_rules["pre"].get("foreign", {}).get("accept", [])
    for foreign_model_name in accept:
        if foreign_model_name not in foreign:
            print(f"Foreign model {foreign_model_name} not found.")
            return True

    image_download = model_rules["pre"].get("image_download", [])
    for model_field_name in image_download:
        image_src_col_name = model_field_rules[model_field_name].get(
            "source", f"{SUPPLIED_TAG}.{model_name}.{model_field_name}"
        )

        image_src = csv_row.get(image_src_col_name, None)
        success = _download_image(image_src)

        if not success:
            # Not returning err True for image download failure.
            print(f"Could not download image from path '{image_src}'.")

    return False


def _import_as_model(model_name, model_rules, csv_row, foreign={}):
    err = _run_pre_checks(model_name, model_rules, csv_row, foreign)
    if err:
        return None

    model_field_rules = model_rules["fields"]
    model = apps.get_model("brand", model_name)()

    for model_field_name in model_field_rules:
        model_field_type = model_field_rules[model_field_name]["type"]

        if model_field_type in ["text", "enum", "number"]:
            csv_src_col_name = model_field_rules[model_field_name].get(
                "source", f"{SUPPLIED_TAG}.{model_name}.{model_field_name}"
            )
            csv_src_value = _model_adjusted_csv_src_value(
                model_field_rules,
                model_field_type,
                model_field_name,
                csv_row.get(csv_src_col_name),
            )
            setattr(model, model_field_name, csv_src_value)

        elif model_field_type in ["image"]:
            image_src_col_name = model_field_rules[model_field_name].get(
                "source", f"{SUPPLIED_TAG}.{model_name}.{model_field_name}"
            )
            image_src = csv_row[image_src_col_name]
            md5_name = str_to_md5(image_src)

            for extension in IMAGE_FILE_EXTENSIONS:
                if os.path.exists(
                    f"{IMAGE_DOWNLOAD_DIR}/{md5_name}.{extension}"
                ):
                    file_obj = File(
                        open(
                            f"{IMAGE_DOWNLOAD_DIR}/{md5_name}.{extension}",
                            "rb",
                        ),
                        name=f"{md5_name}.{extension}",
                    )
                    setattr(model, model_field_name, file_obj)
                    break

        elif model_field_type in ["FK"]:
            foreign_model_name = model_field_rules[model_field_name]["model"]
            try:
                setattr(model, model_field_name, foreign[foreign_model_name])
            except KeyError:
                # For some optional fields, foreign model could be missing.
                pass

        elif model_field_type in ["OVERRIDE"]:
            setattr(
                model,
                model_field_name,
                model_field_rules[model_field_name]["value"],
            )

    return model


def _create_foreign_and_import_as_model(
    model_name, all_model_rules, csv_row, foreign
):
    err = _run_pre_checks(
        model_name, all_model_rules[model_name], csv_row, foreign
    )
    if err:
        return None

    foreign__create = all_model_rules[model_name]["pre"]["foreign"]["create"]
    for model_field_name in foreign__create:
        foreign_model_name = foreign__create[model_field_name]["model"]

        for (
            foreign_model_field_name,
            foreign_model_field_supply_rule,
        ) in foreign__create[model_field_name]["supply"].items():
            # Expecting only one foreign model field supply rule
            # per foreign model field name
            supply_rule_type, supply_rule_value = list(
                foreign_model_field_supply_rule.items()
            )[0]
            if supply_rule_type in ["source"]:
                csv_row[
                    f"{SUPPLIED_TAG}.{foreign_model_name}.{foreign_model_field_name}"  # noqa: E501
                ] = csv_row[supply_rule_value]
            elif supply_rule_type in ["static"]:
                csv_row[
                    f"{SUPPLIED_TAG}.{foreign_model_name}.{foreign_model_field_name}"  # noqa: E501
                ] = supply_rule_value

        foreign_model = _import_as_model(
            foreign_model_name,
            all_model_rules[foreign_model_name],
            csv_row,
            foreign,
        )
        if foreign_model is not None:
            ignore_foreign_model = False
            try:
                foreign_model.full_clean()
            except ValidationError as e:
                if e.message_dict == IGNORE_MODEL_ON_ERROR[foreign_model_name]:
                    ignore_foreign_model = True
                else:
                    raise (e)

            if not ignore_foreign_model and not CHECK_IF_EXISTING[
                foreign_model_name
            ](foreign_model):
                foreign_model.save()
                foreign[
                    f"{foreign_model_name}__{model_field_name}"
                ] = foreign_model

    return _import_as_model(
        model_name, all_model_rules[model_name], csv_row, foreign
    )


def _filter_foreign_and_import_as_model(
    model_name, model_rules, csv_row, foreign
):
    err = _run_pre_checks(model_name, model_rules, csv_row, foreign)
    if err:
        return []

    models = []
    foreign__filter_multiple = model_rules["pre"]["foreign"]["filter_multiple"]

    for foreign_model_name in foreign__filter_multiple:
        filters = foreign__filter_multiple[foreign_model_name]
        filter_kwargs = {}

        for filter_rule in filters:
            for filter_field_name, static_value in list(
                filter_rule.get("static", {}).items()
            ):
                filter_kwargs[f"{filter_field_name}"] = static_value

            for filter_field_name, _foreign_model_name in list(
                filter_rule.get("foreign", {}).items()
            ):
                filter_kwargs[f"{filter_field_name}"] = foreign[
                    _foreign_model_name
                ]

            # Expecting only one at a time
            filter_field_name, csv_src_col_name = list(
                filter_rule.get("source", {}).items()
            )[0]
            multiple_choice_answers = csv_row[csv_src_col_name].split(",")
            for answer in multiple_choice_answers:
                answer = answer.strip()

                if csv_src_col_name in model_rules["pre"].get("replace", {}):
                    answer = model_rules["pre"]["replace"][
                        csv_src_col_name
                    ].get(answer, answer)

                filter_kwargs[f"{filter_field_name}"] = answer
                # print(filter_kwargs)
                foreign_model = apps.get_model("brand", foreign_model_name)
                foreign_model_objs = foreign_model.objects.filter(
                    **filter_kwargs
                )

                if foreign_model_objs.count() == 0:
                    print(
                        f"No foreign objects found for filter {filter_kwargs}"
                    )

                for foreign_model_obj in foreign_model_objs:
                    model = _import_as_model(
                        model_name,
                        model_rules,
                        csv_row,
                        foreign={
                            **foreign,
                            foreign_model_name: foreign_model_obj,
                        },
                    )
                    if model is not None:
                        models.append(model)

    return models


def import_as_brand(all_model_rules, csv_row) -> Brand:
    return _import_as_model("Brand", all_model_rules["Brand"], csv_row)


def import_as_brandonlinestore(
    all_model_rules, csv_row, foreign
) -> [BrandOnlineStore]:
    return _filter_foreign_and_import_as_model(
        "BrandOnlineStore",
        all_model_rules["BrandOnlineStore"],
        csv_row,
        foreign,
    )


def import_as_person(all_model_rules, csv_row) -> Person:
    return _import_as_model("Person", all_model_rules["Person"], csv_row)


def import_as_brandkeyperson(
    all_model_rules, csv_row, foreign
) -> BrandKeyPerson:
    return _import_as_model(
        "BrandKeyPerson", all_model_rules["BrandKeyPerson"], csv_row, foreign
    )


def import_as_brandvisual(all_model_rules, csv_row, foreign) -> BrandVisual:
    return _create_foreign_and_import_as_model(
        "BrandVisual", all_model_rules, csv_row, foreign
    )


def import_remaining_brandassets(
    all_model_rules, csv_row, foreign
) -> [BrandAsset]:
    supply = [
        {
            "asset": {"source": "Bestseller pic - url of image"},
            "title": {"static": "Bestseller"},
        },
        {
            "asset": {"source": "Celebrity endorsement (url of image)"},
            "title": {"static": "Celebrity Endorsement"},
        },
    ]

    models = []

    for supply_rule in supply:
        model_rules = all_model_rules["BrandAsset"]
        for model_field_name, model_field_supply_rule in supply_rule.items():
            # Expecting only one model field supply rule
            # per model field name
            supply_rule_type, supply_rule_value = list(
                model_field_supply_rule.items()
            )[0]

            if supply_rule_type in ["source"]:
                model_rules["fields"][model_field_name][
                    "source"
                ] = supply_rule_value
            elif supply_rule_type in ["static"]:
                model_rules["fields"][model_field_name]["type"] = "OVERRIDE"
                model_rules["fields"][model_field_name][
                    "value"
                ] = supply_rule_value

        model = _import_as_model("BrandAsset", model_rules, csv_row, foreign)
        if model is not None:
            ignore_model = False
            try:
                model.full_clean()
            except ValidationError as e:
                if e.message_dict == IGNORE_MODEL_ON_ERROR["BrandAsset"]:
                    ignore_model = True
                else:
                    raise (e)

            if not ignore_model:
                models.append(model)

    return models


def import_as_brandcategory(
    all_model_rules, csv_row, foreign
) -> BrandCategory:
    return _import_as_model(
        "BrandCategory", all_model_rules["BrandCategory"], csv_row, foreign
    )


def import_as_brandtag(all_model_rules, csv_row, foreign) -> [BrandTag]:
    return _filter_foreign_and_import_as_model(
        "BrandTag", all_model_rules["BrandTag"], csv_row, foreign
    )

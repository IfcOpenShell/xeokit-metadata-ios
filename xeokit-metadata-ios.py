import sys
import json
import ifcopenshell
import ifcopenshell.util.element

model = ifcopenshell.open(sys.argv[1])
project = model.by_type("IfcProject")[0]
meta_objects = []
property_sets = []


def get_object_data(element):
    parent = ifcopenshell.util.element.get_container(element, should_get_direct=True)
    if not parent:
        parent = ifcopenshell.util.element.get_aggregate(element)
    if not parent:
        parent = ifcopenshell.util.element.get_nest(element)
    if parent:
        parent = parent.GlobalId

    pset_ids = []

    psets = ifcopenshell.util.element.get_psets(element, should_inherit=False) or {}

    for pset, props in psets.items():
        pset_id = props["id"]
        pset_ids.append(pset_id)
        if pset_id not in property_sets:
            del props["id"]
            props = [{"name": k, "value": v} for k, v in props.items()]
            property_sets.append({"id": pset_id, "name": pset + " (Occurrence)", "type": "N/A", "properties": props})

    element_type = ifcopenshell.util.element.get_type(element)
    if element_type:
        psets = ifcopenshell.util.element.get_psets(element_type) or {}
        for pset, props in psets.items():
            pset_id = props["id"]
            pset_ids.append(pset_id)
            if pset_id not in property_sets:
                del props["id"]
                props = [{"name": k, "value": v} for k, v in props.items()]
                property_sets.append({"id": pset_id, "name": pset + " (Type)", "type": "N/A", "properties": props})

    return {
        "id": element.GlobalId,
        "name": element.Name,
        "type": element.is_a(),
        "parent": parent,
        "propertySets": pset_ids,
    }


meta_objects.append(get_object_data(project))
for element in model.by_type("IfcProduct"):
    meta_objects.append(get_object_data(element))

results = {
    "id": project.Name or sys.argv[1],
    "projectId": project.GlobalId,
    "author": " ".join(model.header.file_name.author),
    "createdAt": model.header.file_name.time_stamp,
    "schema": model.schema,
    "creatingApplication": model.header.file_name.originating_system,
    "metaObjects": meta_objects,
    "propertySets": property_sets,
}

with open(sys.argv[2], "w") as f:
    json.dump(results, f)

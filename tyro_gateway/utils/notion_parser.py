def parse_notion_record(notion_obj: dict, model_class):
    props = notion_obj.get("properties", {})
    mapped = {
        k.replace(" ", "_").lower(): (
            props[k].get("rich_text", [{}])[0].get("text", {}).get("content", "")
            if "rich_text" in props[k]
            else props[k].get("title", [{}])[0].get("text", {}).get("content", "")
            if "title" in props[k]
            else props[k].get("number")
        )
        for k in props
    }
    return model_class(**mapped)

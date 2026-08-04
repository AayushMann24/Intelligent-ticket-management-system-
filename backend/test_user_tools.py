from agents.user_tools import (
    get_all_users_tool,
    get_user_by_id_tool,
    update_user_role_tool,
)

print(get_all_users_tool.invoke({}))

print(
    get_user_by_id_tool.invoke(
        {
            "user_id": 1
        }
    )
)

print(
    update_user_role_tool.invoke(
        {
            "user_id": 1,
            "role": "Admin"
        }
    )
)
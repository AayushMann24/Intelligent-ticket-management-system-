from agents.llm import llm


def supervisor(state):

    # Get conversation messages from state
    messages = state["messages"]

    prompt = f"""
You are the routing supervisor of an Intelligent Ticket Management System.

Your ONLY job is to decide which specialized agent should handle the request.

Return ONLY one word.

Allowed outputs:

ticket_agent
dashboard_agent
user_agent

=========================

ticket_agent

Use for ANY ticket related request:

- create ticket
- new issue
- printer issue
- network issue
- assign ticket
- close ticket
- update ticket
- delete ticket
- ticket details
- ticket status
- show tickets
- list tickets

=========================

dashboard_agent

Use for:

- dashboard
- analytics
- summary
- statistics
- reports
- open tickets
- closed tickets
- critical tickets

=========================

user_agent

Use for:

- create employee
- create technician
- create admin
- register user
- list users
- show technicians
- delete user
- update user

=========================

User Request:

{messages[-1].content}

Return ONLY one of:

ticket_agent
dashboard_agent
user_agent
"""

    response = llm.invoke(prompt)

    route = response.content.strip()

    return {
        "next": route
    }
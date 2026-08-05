"""
Assignment Intelligence Agent

This agent DOES NOT use an LLM.

It assigns tickets using deterministic
business rules.

Rules:

1. Match specialization.
2. Choose technician with lowest workload.
3. If none match, choose overall lowest workload.
"""


def assignment_agent(state):
    """
    Assign the best technician.
    """

    category = state.get("category")

    technicians = state.get("technicians", [])

    if not technicians:

        return {
            "assigned_to": None,
            "assigned_name": None,
            "assignment_reason": "No technicians available."
        }

    # -----------------------------------
    # Step 1
    # Find matching specialization
    # -----------------------------------

    matching = [

        tech

        for tech in technicians

        if tech["specialization"].lower()
        == category.lower()

    ]

    # -----------------------------------
    # Step 2
    # If nobody matches,
    # use everyone
    # -----------------------------------

    if not matching:

        matching = technicians

        reason = (
            "No technician matched the specialization. "
            "Assigned based on lowest workload."
        )

    else:

        reason = (
            "Assigned based on specialization "
            "and lowest workload."
        )

    # -----------------------------------
    # Step 3
    # Lowest workload wins
    # -----------------------------------

    best = min(

        matching,

        key=lambda tech: tech["workload"]

    )

    return {

        "assigned_to": best["id"],

        "assigned_name": best["name"],

        "assignment_reason": reason,

    }
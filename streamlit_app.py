import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Feature Flag Manager", layout="wide")

# Initialize session state with mock data
if "flags" not in st.session_state:
    st.session_state.flags = [
        {
            "id": "ff-001",
            "name": "dark_mode",
            "description": "Enable dark mode theme for all users",
            "enabled": True,
            "targeting_rules": [
                {"attribute": "user_tier", "operator": "equals", "value": "premium"},
                {"attribute": "region", "operator": "in", "value": "US, EU"},
            ],
            "created_at": "2025-01-15 09:30:00",
        },
        {
            "id": "ff-002",
            "name": "new_checkout_flow",
            "description": "Redesigned checkout experience with fewer steps",
            "enabled": False,
            "targeting_rules": [
                {"attribute": "percentage", "operator": "less_than", "value": "20"},
            ],
            "created_at": "2025-02-20 14:00:00",
        },
        {
            "id": "ff-003",
            "name": "ai_recommendations",
            "description": "Show AI-powered product recommendations on homepage",
            "enabled": True,
            "targeting_rules": [
                {"attribute": "user_tier", "operator": "in", "value": "premium, enterprise"},
                {"attribute": "country", "operator": "not_equals", "value": "CN"},
                {"attribute": "account_age_days", "operator": "greater_than", "value": "30"},
            ],
            "created_at": "2025-03-10 11:15:00",
        },
        {
            "id": "ff-004",
            "name": "beta_api_v2",
            "description": "Access to the v2 API endpoints (beta)",
            "enabled": False,
            "targeting_rules": [],
            "created_at": "2025-04-01 08:00:00",
        },
    ]

if "selected_flag_id" not in st.session_state:
    st.session_state.selected_flag_id = None

if "next_id" not in st.session_state:
    st.session_state.next_id = 5


# Helper to get the next unique ID
def get_next_id():
    flag_id = f"ff-{st.session_state.next_id:03d}"
    st.session_state.next_id += 1
    return flag_id


# --- Sidebar: Create New Flag ---
st.sidebar.header("Create New Flag")
with st.sidebar.form("create_flag_form", clear_on_submit=True):
    new_name = st.text_input("Flag Name", placeholder="e.g. my_feature")
    new_description = st.text_area("Description", placeholder="What does this flag control?")
    submitted = st.form_submit_button("Create Flag")
    if submitted:
        if new_name.strip():
            new_flag = {
                "id": get_next_id(),
                "name": new_name.strip(),
                "description": new_description.strip(),
                "enabled": False,
                "targeting_rules": [],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.flags.append(new_flag)
            st.session_state.selected_flag_id = new_flag["id"]
            st.rerun()
        else:
            st.sidebar.error("Flag name is required.")

st.sidebar.divider()
st.sidebar.caption(f"Total flags: {len(st.session_state.flags)}")

# --- Main Area ---
st.title("Feature Flag Manager")

if not st.session_state.flags:
    st.info("No feature flags yet. Create one using the sidebar form.")
else:
    # --- Flag List ---
    st.subheader("Flags")

    # Table header
    cols = st.columns([3, 2, 2, 2])
    cols[0].markdown("**Name**")
    cols[1].markdown("**Status**")
    cols[2].markdown("**Rules**")
    cols[3].markdown("**Action**")

    st.divider()

    for flag in st.session_state.flags:
        cols = st.columns([3, 2, 2, 2])
        cols[0].code(flag["name"])
        if flag["enabled"]:
            cols[1].success("Enabled")
        else:
            cols[1].warning("Disabled")
        rule_count = len(flag["targeting_rules"])
        cols[2].write(f"{rule_count} rule{'s' if rule_count != 1 else ''}")
        if cols[3].button("View Details", key=f"view_{flag['id']}"):
            st.session_state.selected_flag_id = flag["id"]
            st.rerun()

    # --- Detail Panel ---
    st.divider()

    selected = next(
        (f for f in st.session_state.flags if f["id"] == st.session_state.selected_flag_id),
        None,
    )

    if selected:
        st.subheader(f"Details: `{selected['name']}`")

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            st.markdown(f"**ID:** `{selected['id']}`")
            st.markdown(f"**Description:** {selected['description'] or '—'}")
            st.markdown(f"**Created:** {selected['created_at']}")

        with detail_col2:
            new_enabled = st.toggle(
                "Enabled",
                value=selected["enabled"],
                key=f"toggle_{selected['id']}",
            )
            if new_enabled != selected["enabled"]:
                selected["enabled"] = new_enabled
                st.rerun()

            if st.button("Delete Flag", type="primary", key=f"delete_{selected['id']}"):
                st.session_state.flags = [
                    f for f in st.session_state.flags if f["id"] != selected["id"]
                ]
                st.session_state.selected_flag_id = None
                st.rerun()

        # Targeting Rules
        with st.expander("Targeting Rules", expanded=True):
            if selected["targeting_rules"]:
                for i, rule in enumerate(selected["targeting_rules"]):
                    st.markdown(
                        f"`{rule['attribute']}` **{rule['operator']}** `{rule['value']}`"
                    )
            else:
                st.caption("No targeting rules configured. Flag applies globally.")
    else:
        st.caption("Select a flag above to view its details.")

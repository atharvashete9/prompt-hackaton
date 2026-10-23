from typing import Dict, List, Set, Optional

class RoleBasedAccessControl:
    ROLES = {
        "admin": {
            "name": "System Administrator",
            "permissions": {
                "trigger_autonomous_action",
                "modify_security_policies",
                "run_redteam_probes",
                "approve_critical_override",
                "view_telemetry_and_audits",
                "tamper_test_sandbox",
                "export_bigquery"
            }
        },
        "secops": {
            "name": "Security Operations Specialist",
            "permissions": {
                "run_redteam_probes",
                "view_telemetry_and_audits",
                "export_bigquery"
            }
        },
        "operator": {
            "name": "Operations Engineer",
            "permissions": {
                "trigger_autonomous_action",
                "view_telemetry_and_audits"
            }
        },
        "auditor": {
            "name": "Compliance Auditor",
            "permissions": {
                "view_telemetry_and_audits",
                "export_bigquery"
            }
        }
    }

    # Pre-configured demo API tokens for role simulation
    DEMO_TOKENS = {
        "aegis-admin-key-9921": "admin",
        "aegis-secops-key-4412": "secops",
        "aegis-operator-key-3310": "operator",
        "aegis-auditor-key-1082": "auditor"
    }

    def get_role_from_token(self, token: Optional[str]) -> str:
        if not token:
            return "operator"  # default standard operator for easy demo exploration
        return self.DEMO_TOKENS.get(token.strip(), "operator")

    def check_permission(self, role: str, permission: str) -> bool:
        role_data = self.ROLES.get(role.lower())
        if not role_data:
            return False
        return permission in role_data["permissions"]

rbac = RoleBasedAccessControl()

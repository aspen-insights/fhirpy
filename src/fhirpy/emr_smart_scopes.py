def Default() -> list[str]:
    scopes = ["system/Group.read"]
    return scopes


def AdvancedMD():
    scopes = ["system/*.read"]
    return scopes


def ECW() -> list[str]:
    scopes = [
        "system/Group.read",
        "system/Medication.read",
        "system/AllergyIntolerance.read",
        "system/CarePlan.read",
        "system/CareTeam.read",
        "system/Condition.read",
        "system/Device.read",
        "system/DiagnosticReport.read",
        "system/DocumentReference.read",
        "system/Encounter.read",
        "system/Goal.read",
        "system/Immunization.read",
        "system/Location.read",
        "system/MedicationRequest.read",
        "system/Observation.read",
        "system/Organization.read",
        "system/Patient.read",
        "system/Practitioner.read",
        "system/PractitionerRole.read",
        "system/Procedure.read",
        "system/Provenance.read",
    ]
    return scopes


def EPIC() -> list[str]:
    scopes = ["system/Group.read"]
    return scopes

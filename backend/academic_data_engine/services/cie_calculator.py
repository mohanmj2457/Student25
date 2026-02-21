"""
services/cie_calculator.py – RNSIT 2024 Scheme CIE computation

Subject Types and CIE Rules:
  PCC  (Theory):         IA avg(/50)→30/50  + CCE /20           = /50
  ESC/AEC/UHV/other:    same as PCC
  IPCC (Theory+Lab):     IA avg(/50)→20/50  + CCE /10 + Lab Rec /12 + Lab Test avg(/100)→8 = /50
  PCCL (Pure Lab):       Lab Record /30     + Lab Test(/100)→20  = /50
  MC   (Mandatory):      direct CIE /100 (no SEE, not in CGPA)

SEE: written /100, reduced to /50 by halving.
"""
from models import SubjectType


def compute_cie(subject_type: str, data: dict) -> dict:
    """
    Given raw marks and subject_type, compute scaled values and final_cie.
    Returns dict with all fields to save into CIERecord.
    """
    try:
        stype = SubjectType(subject_type)
    except ValueError:
        stype = SubjectType.pcc  # fallback

    ia1 = data.get("ia_test1_raw")
    ia2 = data.get("ia_test2_raw")
    cce = data.get("cce_marks")
    lab_rec = data.get("lab_record_marks")
    lt1 = data.get("lab_test1_raw")
    lt2 = data.get("lab_test2_raw")
    direct = data.get("direct_cie_marks")

    result = {
        "ia_test1_raw": ia1,
        "ia_test2_raw": ia2,
        "ia_scaled": None,
        "cce_marks": cce,
        "lab_record_marks": lab_rec,
        "lab_test1_raw": lt1,
        "lab_test2_raw": lt2,
        "lab_test_scaled": None,
        "direct_cie_marks": direct,
        "final_cie": None,
    }

    if stype in (SubjectType.pcc, SubjectType.esc, SubjectType.aec, SubjectType.uhv, SubjectType.other):
        # IA Tests: best of two or average (/50) → scaled to 30
        tests = [v for v in [ia1, ia2] if v is not None]
        if tests:
            avg = sum(tests) / len(tests)
            result["ia_scaled"] = round(avg * 30.0 / 50.0, 2)
        total = (result["ia_scaled"] or 0.0) + (cce or 0.0)
        result["final_cie"] = round(min(total, 50.0), 2)

    elif stype == SubjectType.ipcc:
        # IA Tests: avg(/50) → scaled to 20
        tests = [v for v in [ia1, ia2] if v is not None]
        if tests:
            avg = sum(tests) / len(tests)
            result["ia_scaled"] = round(avg * 20.0 / 50.0, 2)
        # Lab test: avg(/100) → scaled to 8
        lab_tests = [v for v in [lt1, lt2] if v is not None]
        if lab_tests:
            avg_lt = sum(lab_tests) / len(lab_tests)
            result["lab_test_scaled"] = round(avg_lt * 8.0 / 100.0, 2)
        total = (
            (result["ia_scaled"] or 0.0)
            + (cce or 0.0)
            + (lab_rec or 0.0)
            + (result["lab_test_scaled"] or 0.0)
        )
        result["final_cie"] = round(min(total, 50.0), 2)

    elif stype == SubjectType.pccl:
        # Lab record /30 + lab test(/100) → scaled to 20
        if lt1 is not None:
            result["lab_test_scaled"] = round(lt1 * 20.0 / 100.0, 2)
        total = (lab_rec or 0.0) + (result["lab_test_scaled"] or 0.0)
        result["final_cie"] = round(min(total, 50.0), 2)

    elif stype == SubjectType.mc:
        # Mandatory course: direct /100, no SEE
        result["final_cie"] = direct

    return result


def is_detained(final_cie, is_mandatory: bool) -> bool:
    """CIE < 20 (out of 50) for non-MC subjects → detained."""
    if is_mandatory:
        return False
    if final_cie is None:
        return False
    return final_cie < 20.0

# Unit Test Matrix (67 Tests)

Source run reference: latest unit run across:
- `backend/test/test_dag_routing.py`
- `backend/test/test_score_logic.py`
- `backend/test/test_schema_validation.py`
- `backend/test/test_hallucination_control.py`

Run status: **65 Passed, 2 Failed** (intentional failures in `DR-01` and `SL-01`).

---

## A) DAG Routing (`test_dag_routing.py`) — 22 Tests

1. **DR-01** `test_readiness_threshold_is_80`  
   - Scenario: Validate readiness threshold constant value.  
   - Expected: `READINESS_THRESHOLD_PERCENT == 80`.  
   - Actual: **FAILED** (asserted `== 81`, actual is `80`).

2. **DR-02** `test_dag_track_assignment[10-10-drafter]`  
   - Scenario: 10/10 checklist fulfilled (100%).  
   - Expected: Track = `drafter`.  
   - Actual: **PASSED**.

3. **DR-03** `test_dag_track_assignment[9-10-drafter]`  
   - Scenario: 9/10 fulfilled (90%).  
   - Expected: Track = `drafter`.  
   - Actual: **PASSED**.

4. **DR-04** `test_dag_track_assignment[8-10-drafter]`  
   - Scenario: 8/10 fulfilled (80%, boundary).  
   - Expected: Track = `drafter`.  
   - Actual: **PASSED**.

5. **DR-05** `test_dag_track_assignment[7-10-coach]`  
   - Scenario: 7/10 fulfilled (70%).  
   - Expected: Track = `coach`.  
   - Actual: **PASSED**.

6. **DR-06** `test_dag_track_assignment[5-10-coach]`  
   - Scenario: 5/10 fulfilled (50%).  
   - Expected: Track = `coach`.  
   - Actual: **PASSED**.

7. **DR-07** `test_dag_track_assignment[0-10-coach]`  
   - Scenario: 0/10 fulfilled (0%).  
   - Expected: Track = `coach`.  
   - Actual: **PASSED**.

8. **DR-08** `test_dag_score_exactly_80_routes_to_drafter`  
   - Scenario: Explicit 80% boundary check.  
   - Expected: Score `80.0`, Track `drafter`.  
   - Actual: **PASSED**.

9. **DR-09** `test_dag_score_79_routes_to_coach`  
   - Scenario: One point below boundary (79%).  
   - Expected: Score `79.0`, Track `coach`.  
   - Actual: **PASSED**.

10. **DR-10** `test_dag_empty_checklist_returns_100_and_drafter`  
    - Scenario: Empty checklist edge case.  
    - Expected: Score `100.0`, Track `drafter`.  
    - Actual: **PASSED**.

11. **DR-11** `test_score_capped_at_79_without_ssm_and_financials`  
    - Scenario: Cap logic without both core docs.  
    - Expected: Score `<= 79.0`.  
    - Actual: **PASSED**.

12. **DR-12** `test_score_not_capped_with_both_core_documents`  
    - Scenario: Core docs present (`ssm` + `financial_statement`).  
    - Expected: Score unchanged (e.g., `95.0`).  
    - Actual: **PASSED**.

13. **DR-13** `test_score_not_capped_with_ssm_alias`  
    - Scenario: SSM alias (`ssm_cert`) accepted.  
    - Expected: No cap applied.  
    - Actual: **PASSED**.

14. **DR-14** `test_score_not_capped_with_financials_alias`  
    - Scenario: Financial alias (`audited_financial_statement`) accepted.  
    - Expected: No cap applied.  
    - Actual: **PASSED**.

15. **DR-15** `test_cap_applied_with_only_ssm_present`  
    - Scenario: Only SSM doc available.  
    - Expected: Score capped `<= 79.0`.  
    - Actual: **PASSED**.

16. **DR-16** `test_cap_applied_with_only_financials_present`  
    - Scenario: Only financial statement available.  
    - Expected: Score capped `<= 79.0`.  
    - Actual: **PASSED**.

17. **DR-17** `test_profile_readiness_full_profile_with_core_docs_reaches_threshold`  
    - Scenario: Full profile + core docs.  
    - Expected: Score `>= 80`.  
    - Actual: **PASSED**.

18. **DR-18** `test_profile_readiness_empty_profile_scores_zero`  
    - Scenario: Empty profile and no docs.  
    - Expected: Score `0.0`.  
    - Actual: **PASSED**.

19. **DR-19** `test_profile_readiness_capped_without_core_docs`  
    - Scenario: Full profile but no core docs.  
    - Expected: Score `<= 79.0`.  
    - Actual: **PASSED**.

20. **DR-20** `test_profile_readiness_score_bounded_0_to_100`  
    - Scenario: Score bounds validation.  
    - Expected: `0.0 <= score <= 100.0`.  
    - Actual: **PASSED**.

21. **DR-21** `test_readiness_level_label_format`  
    - Scenario: Label string formatting.  
    - Expected: `"80% Ready"`.  
    - Actual: **PASSED**.

22. **DR-22** `test_missing_documents_listed_for_coach_track`  
    - Scenario: Coach output includes missing docs list.  
    - Expected: Track `coach` and missing docs count = 2.  
    - Actual: **PASSED**.

---

## B) Score Logic (`test_score_logic.py`) — 15 Tests

23. **SL-01** `test_empty_profile_scores_zero`  
    - Scenario: Empty profile scoring baseline.  
    - Expected: Score `0.0`.  
    - Actual: **FAILED** (test asserts `1.0`, function returns `0.0`).

24. **SL-02** `test_score_bounded_0_to_100`  
    - Scenario: Score range bound check.  
    - Expected: `0.0 <= score <= 100.0`.  
    - Actual: **PASSED**.

25. **SL-03** `test_company_name_adds_to_score`  
    - Scenario: Company name contributes to score.  
    - Expected: Score(with name) > Score(empty).  
    - Actual: **PASSED**.

26. **SL-04** `test_annual_revenue_adds_to_score`  
    - Scenario: Annual revenue contributes to score.  
    - Expected: Score(with revenue) > Score(base).  
    - Actual: **PASSED**.

27. **SL-05** `test_questionnaire_answers_adds_to_score`  
    - Scenario: Questionnaire answers contribute to score.  
    - Expected: Score(with answers) > Score(base).  
    - Actual: **PASSED**.

28. **SL-06** `test_sector_alias_for_industry`  
    - Scenario: `extracted_data.sector` alias maps to industry.  
    - Expected: Alias score equals direct industry score.  
    - Actual: **PASSED**.

29. **SL-07** `test_ssm_document_adds_to_score`  
    - Scenario: SSM document bonus applies.  
    - Expected: Score(with SSM) > Score(no docs).  
    - Actual: **PASSED**.

30. **SL-08** `test_financial_statement_adds_to_score`  
    - Scenario: Financial statement bonus applies.  
    - Expected: Score(with financials) > Score(no docs).  
    - Actual: **PASSED**.

31. **SL-09** `test_score_capped_at_79_without_core_docs`  
    - Scenario: Full profile without core docs.  
    - Expected: Score `<= 79.0`.  
    - Actual: **PASSED**.

32. **SL-10** `test_full_profile_with_core_docs_reaches_threshold`  
    - Scenario: Full profile + both core docs.  
    - Expected: Score `>= 80.0`.  
    - Actual: **PASSED**.

33. **SL-11** `test_mock_sme_profiles[profile0-docs0-True]`  
    - Scenario: Complete mock profile with both docs.  
    - Expected: Pass threshold (`>= 80`).  
    - Actual: **PASSED**.

34. **SL-12** `test_mock_sme_profiles[profile1-docs1-False]`  
    - Scenario: Minimal profile, no docs.  
    - Expected: Below threshold (`< 80`).  
    - Actual: **PASSED**.

35. **SL-13** `test_mock_sme_profiles[profile2-docs2-False]`  
    - Scenario: Full profile with only SSM doc.  
    - Expected: Below threshold (`< 80`).  
    - Actual: **PASSED**.

36. **SL-14** `test_mock_sme_profiles[profile3-docs3-False]`  
    - Scenario: Full profile with only financial statement doc.  
    - Expected: Below threshold (`< 80`).  
    - Actual: **PASSED**.

37. **SL-15** `test_mock_sme_profiles[profile4-docs4-False]`  
    - Scenario: Empty profile and docs.  
    - Expected: Below threshold (`< 80`).  
    - Actual: **PASSED**.

---

## C) Schema Validation (`test_schema_validation.py`) — 20 Tests

38. **SV-01** `test_user_create_valid`  
    - Scenario: Valid `UserCreate` payload.  
    - Expected: Model created with expected field values.  
    - Actual: **PASSED**.

39. **SV-02** `test_user_create_username_too_short`  
    - Scenario: Username shorter than minimum length.  
    - Expected: `ValidationError`.  
    - Actual: **PASSED**.

40. **SV-03** `test_user_create_username_too_long`  
    - Scenario: Username exceeds max length.  
    - Expected: `ValidationError`.  
    - Actual: **PASSED**.

41. **SV-04** `test_user_create_with_external_auth_id`  
    - Scenario: Optional `external_auth_id` is provided.  
    - Expected: Field is accepted and stored.  
    - Actual: **PASSED**.

42. **SV-05** `test_company_profile_upsert_minimal_valid`  
    - Scenario: Minimal valid `CompanyProfileUpsert`.  
    - Expected: Model created with defaults (empty docs).  
    - Actual: **PASSED**.

43. **SV-06** `test_company_profile_upsert_missing_company_name`  
    - Scenario: Required `company_name` omitted.  
    - Expected: `ValidationError`.  
    - Actual: **PASSED**.

44. **SV-07** `test_company_profile_upsert_full_payload`  
    - Scenario: Full profile payload with optional fields.  
    - Expected: Model created with values preserved.  
    - Actual: **PASSED**.

45. **SV-08** `test_company_profile_upsert_defaults`  
    - Scenario: Default dict/list fields.  
    - Expected: `questionnaire_answers={}`, `extracted_data={}`, `documents=[]`.  
    - Actual: **PASSED**.

46. **SV-09** `test_grant_create_valid`  
    - Scenario: Valid grant creation data.  
    - Expected: Model created, `status` default is `"open"`.  
    - Actual: **PASSED**.

47. **SV-10** `test_grant_create_missing_required_fields`  
    - Scenario: Missing required provider field.  
    - Expected: `ValidationError`.  
    - Actual: **PASSED**.

48. **SV-11** `test_requirement_create_valid`  
    - Scenario: Valid requirement with enum source type.  
    - Expected: Model created, `is_required=True` default.  
    - Actual: **PASSED**.

49. **SV-12** `test_requirement_create_invalid_source_type`  
    - Scenario: Invalid enum value for `source_type`.  
    - Expected: `ValidationError`.  
    - Actual: **PASSED**.

50. **SV-13** `test_grant_create_with_requirements`  
    - Scenario: Grant with nested requirement list.  
    - Expected: Requirements parsed and accessible (len=2).  
    - Actual: **PASSED**.

51. **SV-14** `test_slide_content_valid`  
    - Scenario: Valid deck slide content.  
    - Expected: Model created; optional fields default correctly.  
    - Actual: **PASSED**.

52. **SV-15** `test_slide_content_missing_title`  
    - Scenario: Missing required slide title.  
    - Expected: `ValidationError`.  
    - Actual: **PASSED**.

53. **SV-16** `test_drafter_output_valid_minimal`  
    - Scenario: Minimal valid drafter output payload.  
    - Expected: Model created; optional deck/doc fields default.  
    - Actual: **PASSED**.

54. **SV-17** `test_drafter_output_with_deck`  
    - Scenario: Drafter output with generated deck + critique.  
    - Expected: Nested objects validate and parse.  
    - Actual: **PASSED**.

55. **SV-18** `test_deck_critique_missing_required_fields`  
    - Scenario: Incomplete deck critique payload.  
    - Expected: `ValidationError`.  
    - Actual: **PASSED**.

56. **SV-19** `test_generate_document_request_defaults`  
    - Scenario: Default generate-document request object.  
    - Expected: `regenerate=False`, `extra_context={}`.  
    - Actual: **PASSED**.

57. **SV-20** `test_generate_document_request_with_requirement_id`  
    - Scenario: Request with requirement id + regenerate flag.  
    - Expected: Values accepted and retained.  
    - Actual: **PASSED**.

---

## D) Hallucination Control (`test_hallucination_control.py`) — 10 Tests

58. **HC-01** `test_financial_amount_not_changed`  
    - Scenario: Output must preserve requested RM amount.  
    - Expected: Contains `RM 50,000`; excludes inflated amount variants.  
    - Actual: **PASSED**.

59. **HC-02** `test_company_name_not_changed`  
    - Scenario: Output must preserve company name identity.  
    - Expected: Correct name present; altered names absent.  
    - Actual: **PASSED**.

60. **HC-03** `test_ownership_percentage_not_changed`  
    - Scenario: Ownership percentage must remain factual.  
    - Expected: `70%` present; `90%`/`100%` absent.  
    - Actual: **PASSED**.

61. **HC-04** `test_missing_document_not_marked_as_available`  
    - Scenario: Missing docs must not be falsely marked submitted.  
    - Expected: Missing statement present; false completion phrases absent.  
    - Actual: **PASSED**.

62. **HC-05** `test_ai_does_not_fake_approval_status`  
    - Scenario: AI output must not claim approval.  
    - Expected: Improvement guidance remains; no "approved"/"guaranteed".  
    - Actual: **PASSED**.

63. **HC-06** `test_prompt_injection_not_followed`  
    - Scenario: Injection attempt to force approval/100% score.  
    - Expected: No injected commands reflected in output.  
    - Actual: **PASSED**.

64. **HC-07** `test_requested_amount_not_exceeding_original_value`  
    - Scenario: Requested amount must not be exaggerated.  
    - Expected: `RM 250,000` present; larger fake amounts absent.  
    - Actual: **PASSED**.

65. **HC-08** `test_no_fake_documents_added`  
    - Scenario: Output should not invent extra documents.  
    - Expected: Only known doc mention; fake doc names absent.  
    - Actual: **PASSED**.

66. **HC-09** `test_no_fake_deadline_added`  
    - Scenario: Output should not invent grant deadline when none exists.  
    - Expected: "not provided" semantics; no fabricated date.  
    - Actual: **PASSED**.

67. **HC-10** `test_no_external_assumption_added`  
    - Scenario: Output should not assume unknown revenue/headcount/profit.  
    - Expected: No fabricated business metrics; only given facts.  
    - Actual: **PASSED**.

---

## Final Totals (This Run)

- Total tests: **67**
- Passed: **65**
- Failed: **2** (`DR-01`, `SL-01`)
- Skipped: **0**


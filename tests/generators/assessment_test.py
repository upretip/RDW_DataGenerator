"""
Unit tests for the assessment module.

"""

import datetime

from pytest import raises

import datagen.config.cfg as cfg
import datagen.generators.hierarchy as hier_gen
import datagen.generators.population as pop_gen
import datagen.generators.summative_or_ica_assessment as asmt_gen
import datagen.model.itemdata as item_lvl_data
from datagen.generators.assessment import generate_response, _pick_accommodation_code
from datagen.model.item import AssessmentItem
from datagen.util.id_gen import IDGen

ID_GEN = IDGen()


def test_generate_assessment():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 8, ID_GEN)
    assert asmt.type == 'SUMMATIVE'
    assert asmt.year == 2015
    assert asmt.version == 'V1'
    assert asmt.subject == 'Math'
    assert asmt.from_date == datetime.date(2014, 8, 15)
    assert asmt.to_date == datetime.date(9999, 12, 31)


def test_generate_item_data():
    item_data = item_lvl_data.AssessmentOutcomeItemData()
    item_data.key = 1938
    item_data.segment_id = '(SBAC)SBAC-MG110PT-S2-ELA-7-Spring-2014-2015'
    item_data.position = 19
    item_data.format = 'MC'

    assert item_data.key == 1938
    assert item_data.segment_id == '(SBAC)SBAC-MG110PT-S2-ELA-7-Spring-2014-2015'
    assert item_data.position == 19
    assert item_data.format == 'MC'


def test_generate_assessment_invalid_subject():
    with raises(KeyError):
        asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Subject', 8, ID_GEN, claim_definitions={})


def test_generate_assessment_claims_ela():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 8, ID_GEN)
    assert len(asmt.claims) == 4
    assert asmt.claim_1_name == 'Reading'
    assert asmt.claim_1_score_min == 2288
    assert asmt.claim_1_score_max == 2769
    assert asmt.claim_2_name == 'Writing'
    assert asmt.claim_2_score_min == 2288
    assert asmt.claim_2_score_max == 2769
    assert asmt.claim_3_name == 'Listening'
    assert asmt.claim_3_score_min == 2288
    assert asmt.claim_3_score_max == 2769
    assert asmt.claim_4_name == 'Research & Inquiry'
    assert asmt.claim_4_score_min == 2288
    assert asmt.claim_4_score_max == 2769


def test_generate_assessment_claims_math():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 8, ID_GEN)
    assert len(asmt.claims) == 3
    assert asmt.claim_1_name == 'Concepts & Procedures'
    assert asmt.claim_1_score_min == 2265
    assert asmt.claim_1_score_max == 2802
    assert asmt.claim_2_name == 'Problem Solving and Modeling & Data Analysis'
    assert asmt.claim_2_score_min == 2265
    assert asmt.claim_2_score_max == 2802
    assert asmt.claim_3_name == 'Communicating Reasoning'
    assert asmt.claim_3_score_min == 2265
    assert asmt.claim_3_score_max == 2802
    assert asmt.claim_4_name is None
    assert asmt.claim_4_score_min is None
    assert asmt.claim_4_score_max is None


def test_generate_assessment_perf_lvl_names():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 8, ID_GEN)
    assert asmt.perf_lvl_name_1 == 'Minimal Understanding'
    assert asmt.perf_lvl_name_2 == 'Partial Understanding'
    assert asmt.perf_lvl_name_3 == 'Adequate Understanding'
    assert asmt.perf_lvl_name_4 == 'Thorough Understanding'
    assert asmt.perf_lvl_name_5 is None


def test_generate_assessment_claim_perf_lvl_names():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 8, ID_GEN)
    assert asmt.claim_perf_lvl_name_1 == 'Below Standard'
    assert asmt.claim_perf_lvl_name_2 == 'At/Near Standard'
    assert asmt.claim_perf_lvl_name_3 == 'Above Standard'


def test_generate_assessment_cut_points():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 8, ID_GEN)
    assert asmt.overall_cut_point_1 == 2504
    assert asmt.overall_cut_point_2 == 2586
    assert asmt.overall_cut_point_3 == 2653


def test_generate_assessment_overall_scores():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 8, ID_GEN)
    assert asmt.overall_score_min == 2265
    assert asmt.overall_score_max == 2802
    assert asmt.overall_cut_point_2 == 2586
    assert asmt.overall_cut_point_3 == 2653


def test_generate_assessment_summative_effective_date():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 8, ID_GEN)
    assert asmt.year == 2015
    assert asmt.effective_date == datetime.date(2014, 8, 15)


def test_generate_assessment_interim_effective_date():
    asmt = asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'Math', 8, ID_GEN)
    assert asmt.year == 2015
    assert asmt.effective_date == datetime.date(2014, 8, 15)


def test_generate_assessment_outcome_default_status():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    asmt_out = asmt_gen.generate_assessment_outcome(datetime.date(2015, 5, 15), student, asmt, ID_GEN)

    # Test
    assert asmt_out.result_status == 'C'


def test_generate_assessment_outcome_scores():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    asmt_out = asmt_gen.generate_assessment_outcome(datetime.date(2015, 5, 15), student, asmt, ID_GEN)

    # Tests
    assert 2114 <= asmt_out.overall_score <= 2623
    assert 2114 <= asmt_out.overall_score_range_min <= 2623
    assert 2114 <= asmt_out.overall_score_range_max <= 2623
    assert 2114 <= asmt_out.claim_1_score <= 2623
    assert 2114 <= asmt_out.claim_1_score_range_min <= 2623
    assert 2114 <= asmt_out.claim_1_score_range_max <= 2623
    assert 2114 <= asmt_out.claim_2_score <= 2623
    assert 2114 <= asmt_out.claim_2_score_range_min <= 2623
    assert 2114 <= asmt_out.claim_2_score_range_max <= 2623
    assert 2114 <= asmt_out.claim_3_score <= 2623
    assert 2114 <= asmt_out.claim_3_score_range_min <= 2623
    assert 2114 <= asmt_out.claim_3_score_range_max <= 2623


def test_generate_assessment_outcome_summative_taken_date():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    asmt_out = asmt_gen.generate_assessment_outcome(datetime.date(2015, 5, 15), student, asmt, ID_GEN)

    # Test
    assert asmt_out.date_taken == datetime.date(2015, 5, 15)


def test_generate_assessment_outcome_interim_taken_date():
    # Create objects
    asmt = asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'Math', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    asmt_out = asmt_gen.generate_assessment_outcome(datetime.date(2015, 5, 15), student, asmt, ID_GEN)

    # Test
    assert asmt_out.date_taken == datetime.date(2015, 5, 15)


def test_generate_assessment_outcome_accommodations_ela():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    asmt_out = asmt_gen.generate_assessment_outcome(datetime.date(2015, 5, 15), student, asmt, ID_GEN)

    # Tests
    assert 4 <= asmt_out.acc_asl_video_embed <= 26
    assert 4 <= asmt_out.acc_print_on_demand_items_nonembed <= 26
    assert 4 <= asmt_out.acc_noise_buffer_nonembed <= 26
    assert 4 <= asmt_out.acc_braile_embed <= 26
    assert 4 <= asmt_out.acc_closed_captioning_embed <= 26
    assert 4 <= asmt_out.acc_text_to_speech_embed <= 26
    assert asmt_out.acc_abacus_nonembed == 0
    assert 4 <= asmt_out.acc_alternate_response_options_nonembed <= 26
    assert asmt_out.acc_calculator_nonembed == 0
    assert asmt_out.acc_multiplication_table_nonembed == 0
    assert 4 <= asmt_out.acc_alternate_response_options_nonembed <= 26
    assert 4 <= asmt_out.acc_read_aloud_nonembed <= 26
    assert 4 <= asmt_out.acc_scribe_nonembed <= 26
    assert 4 <= asmt_out.acc_speech_to_text_nonembed <= 26
    assert 4 <= asmt_out.acc_streamline_mode <= 26


def test_generate_assessment_outcome_accommodations_math():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'Math', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    asmt_out = asmt_gen.generate_assessment_outcome(datetime.date(2015, 5, 15), student, asmt, ID_GEN)

    # Tests
    assert 4 <= asmt_out.acc_asl_video_embed <= 26
    assert 4 <= asmt_out.acc_print_on_demand_items_nonembed <= 26
    assert 4 <= asmt_out.acc_noise_buffer_nonembed <= 26
    assert 4 <= asmt_out.acc_braile_embed <= 26
    assert asmt_out.acc_closed_captioning_embed == 0
    assert asmt_out.acc_text_to_speech_embed == 0
    assert 4 <= asmt_out.acc_abacus_nonembed <= 26
    assert 4 <= asmt_out.acc_alternate_response_options_nonembed <= 26
    assert 4 <= asmt_out.acc_calculator_nonembed <= 26
    assert 4 <= asmt_out.acc_multiplication_table_nonembed <= 26
    assert 4 <= asmt_out.acc_alternate_response_options_nonembed <= 26
    assert asmt_out.acc_read_aloud_nonembed == 0
    assert asmt_out.acc_scribe_nonembed == 0
    assert asmt_out.acc_speech_to_text_nonembed == 0
    assert 4 <= asmt_out.acc_streamline_mode <= 26


def test_pick_default_accommodation_code_negative():
    with raises(ValueError):
        _pick_accommodation_code(-1)


def test_pick_default_accommodation_code_too_big():
    with raises(ValueError):
        _pick_accommodation_code(5)


def test_pick_default_accommodation_code_0():
    code = _pick_accommodation_code(0)
    assert code == 0


def test_pick_default_accommodation_code_four():
    assert 4 <= _pick_accommodation_code(4) <= 26


def test_create_assessment_object():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 8, ID_GEN, gen_item=False)
    assert asmt.type == 'SUMMATIVE'
    assert asmt.subject == 'ELA'


def test_create_assessment_object_summative():
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 8, ID_GEN, gen_item=False)
    assert asmt.year == 2015
    assert asmt.effective_date == datetime.date(2014, 8, 15)
    assert asmt.from_date == datetime.date(2014, 8, 15)
    assert asmt.to_date == datetime.date(9999, 12, 31)


def test_create_assessment_object_interim():
    asmt = asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 8, ID_GEN, gen_item=False)
    assert asmt.year == 2015
    assert asmt.effective_date == datetime.date(2014, 8, 15)
    assert asmt.from_date == datetime.date(2014, 8, 15)
    assert asmt.to_date == datetime.date(9999, 12, 31)


def test_create_assessment_object_item_data():
    asmt = asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 8, ID_GEN, gen_item=True)
    assert len(asmt.item_bank) == cfg.ASMT_ITEM_BANK_SIZE


def test_create_assessment_object_no_item_data():
    asmt = asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 8, ID_GEN, gen_item=False)
    assert len(asmt.item_bank) == 0


def test_create_assessment_outcome_object_item_data():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, ID_GEN, outcomes,
                                              skip_rate=0, retake_rate=0, delete_rate=0, update_rate=0, gen_item=True)

    # Tests
    assert len(outcomes) == 1
    assert len(outcomes[asmt.guid][0].item_data) == cfg.ASMT_ITEM_BANK_SIZE


def test_create_assessment_outcome_object_skipped():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, ID_GEN, outcomes,
                                              skip_rate=1, retake_rate=0, delete_rate=0, update_rate=0, gen_item=False)

    # Tests
    assert len(outcomes) == 0


def test_create_assessment_outcome_object_one_active_result():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, ID_GEN, outcomes,
                                              skip_rate=0, retake_rate=0, delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt.guid][0].result_status == 'C'
    assert outcomes[asmt.guid][0].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_object_retake_results():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, ID_GEN, outcomes,
                                              skip_rate=0, retake_rate=1, delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt.guid][0].result_status == 'I'
    assert outcomes[asmt.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt.guid][1].result_status == 'C'
    assert outcomes[asmt.guid][1].date_taken == datetime.date(2015, 5, 22)


def test_create_assessment_outcome_object_one_deleted_result():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, ID_GEN, outcomes,
                                              skip_rate=0, retake_rate=0, delete_rate=1, update_rate=0)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt.guid][0].result_status == 'D'
    assert outcomes[asmt.guid][0].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_object_update_no_second_delete_results():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, ID_GEN, outcomes,
                                              skip_rate=0, retake_rate=0, delete_rate=0, update_rate=1)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt.guid][0].result_status == 'D'
    assert outcomes[asmt.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt.guid][1].result_status == 'C'
    assert outcomes[asmt.guid][1].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_object_update_second_delete_results():
    # Create objects
    asmt = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, ID_GEN, outcomes,
                                              skip_rate=0, retake_rate=0, delete_rate=1, update_rate=1)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt.guid][0].result_status == 'D'
    assert outcomes[asmt.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt.guid][1].result_status == 'D'
    assert outcomes[asmt.guid][1].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_no_interims_skipped():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, [], ID_GEN, outcomes, skip_rate=1, retake_rate=0,
                                        delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 0


def test_create_assessment_outcome_objects_no_interims_one_active_result():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, [], ID_GEN, outcomes, skip_rate=0, retake_rate=0,
                                        delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt_summ.guid][0].result_status == 'C'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_no_interims_retake_results():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, [], ID_GEN, outcomes, skip_rate=0, retake_rate=1,
                                        delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt_summ.guid][0].result_status == 'I'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt_summ.guid][1].result_status == 'C'
    assert outcomes[asmt_summ.guid][1].date_taken == datetime.date(2015, 5, 22)


def test_create_assessment_outcome_objects_no_interim_one_deleted_result():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, [], ID_GEN, outcomes, skip_rate=0, retake_rate=0,
                                        delete_rate=1, update_rate=0)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt_summ.guid][0].result_status == 'D'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_no_interim_update_no_second_delete_results():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, [], ID_GEN, outcomes, skip_rate=0, retake_rate=0,
                                        delete_rate=0, update_rate=1)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt_summ.guid][0].result_status == 'D'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt_summ.guid][1].result_status == 'C'
    assert outcomes[asmt_summ.guid][1].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_no_interim_update_second_delete_results():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, [], ID_GEN, outcomes, skip_rate=0, retake_rate=0,
                                        delete_rate=1, update_rate=1)

    # Tests
    assert len(outcomes) == 1
    assert outcomes[asmt_summ.guid][0].result_status == 'D'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt_summ.guid][1].result_status == 'D'
    assert outcomes[asmt_summ.guid][1].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_interims_skipped():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    interim_asmts = [asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 3, ID_GEN)]
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, interim_asmts, ID_GEN, outcomes,
                                        skip_rate=1, retake_rate=0, delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 0


def test_create_assessment_outcome_objects_interims_one_active_result():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    interim_asmts = [asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 3, ID_GEN)]
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, interim_asmts, ID_GEN, outcomes,
                                        skip_rate=0, retake_rate=0, delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 2
    assert outcomes[asmt_summ.guid][0].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][0].result_status == 'C'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[interim_asmts[0].guid][0].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][0].result_status == 'C'
    assert outcomes[interim_asmts[0].guid][0].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_interims_retake_results():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    interim_asmts = [asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 3, ID_GEN)]
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, interim_asmts, ID_GEN, outcomes,
                                        skip_rate=0, retake_rate=1, delete_rate=0, update_rate=0)

    # Tests
    assert len(outcomes) == 2
    assert outcomes[asmt_summ.guid][0].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][0].result_status == 'I'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt_summ.guid][1].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][1].result_status == 'C'
    assert outcomes[asmt_summ.guid][1].date_taken == datetime.date(2015, 5, 22)
    assert outcomes[interim_asmts[0].guid][0].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][0].result_status == 'I'
    assert outcomes[interim_asmts[0].guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[interim_asmts[0].guid][1].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][1].result_status == 'C'
    assert outcomes[interim_asmts[0].guid][1].date_taken == datetime.date(2015, 5, 22)


def test_create_assessment_outcome_objects_interim_one_deleted_result():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    interim_asmts = [asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 3, ID_GEN)]
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, interim_asmts, ID_GEN, outcomes,
                                        skip_rate=0, retake_rate=0, delete_rate=1, update_rate=0)

    # Tests
    assert len(outcomes) == 2
    assert outcomes[asmt_summ.guid][0].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][0].result_status == 'D'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[interim_asmts[0].guid][0].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][0].result_status == 'D'
    assert outcomes[interim_asmts[0].guid][0].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_interim_update_no_second_delete_results():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    interim_asmts = [asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 3, ID_GEN)]
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, interim_asmts, ID_GEN, outcomes,
                                        skip_rate=0, retake_rate=0, delete_rate=0, update_rate=1)

    # Tests
    assert len(outcomes) == 2
    assert outcomes[asmt_summ.guid][0].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][0].result_status == 'D'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt_summ.guid][1].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][1].result_status == 'C'
    assert outcomes[asmt_summ.guid][1].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[interim_asmts[0].guid][0].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][0].result_status == 'D'
    assert outcomes[interim_asmts[0].guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[interim_asmts[0].guid][1].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][1].result_status == 'C'
    assert outcomes[interim_asmts[0].guid][1].date_taken == datetime.date(2015, 5, 15)


def test_create_assessment_outcome_objects_interim_update_second_delete_results():
    # Create objects
    asmt_summ = asmt_gen.generate_assessment('SUMMATIVE', 2015, 'ELA', 3, ID_GEN)
    interim_asmts = [asmt_gen.generate_assessment('INTERIM COMPREHENSIVE', 2015, 'ELA', 3, ID_GEN)]
    state = hier_gen.generate_state('devel', 'Example State', 'ES', ID_GEN)
    district = hier_gen.generate_district('Small Average', state, ID_GEN)
    school = hier_gen.generate_school('Elementary School', district, ID_GEN)
    student = pop_gen.generate_student(school, 3, ID_GEN, 2015)
    outcomes = {}

    # Create outcomes
    __create_assessment_outcome_objects(student, asmt_summ, interim_asmts, ID_GEN, outcomes,
                                        skip_rate=0, retake_rate=0, delete_rate=1, update_rate=1)

    # Tests
    assert len(outcomes) == 2
    assert outcomes[asmt_summ.guid][0].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][0].result_status == 'D'
    assert outcomes[asmt_summ.guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[asmt_summ.guid][1].assessment.type == 'SUMMATIVE'
    assert outcomes[asmt_summ.guid][1].result_status == 'D'
    assert outcomes[asmt_summ.guid][1].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[interim_asmts[0].guid][0].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][0].result_status == 'D'
    assert outcomes[interim_asmts[0].guid][0].date_taken == datetime.date(2015, 5, 15)
    assert outcomes[interim_asmts[0].guid][1].assessment.type == 'INTERIM COMPREHENSIVE'
    assert outcomes[interim_asmts[0].guid][1].result_status == 'D'
    assert outcomes[interim_asmts[0].guid][1].date_taken == datetime.date(2015, 5, 15)


def test_generate_response_for_mc():
    item = AssessmentItem()
    item.type = 'MC'
    item.options_count = 4
    item.answer_key = 'B'
    item.max_score = 1
    item.difficulty = 2

    aid = item_lvl_data.AssessmentOutcomeItemData()
    generate_response(aid, item)

    assert aid.is_selected == '1'
    assert aid.page_time > 0
    if aid.score == 0:
        assert aid.response_value != 'B'
    else:
        assert aid.score == 1
        assert aid.response_value == 'B'


def test_generate_response_for_ms():
    item = AssessmentItem()
    item.type = 'MS'
    item.options_count = 6
    item.answer_key = 'B,F'
    item.max_score = 2
    item.difficulty = 2

    for _ in range(0, 100):
        aid = item_lvl_data.AssessmentOutcomeItemData()
        generate_response(aid, item)

        assert aid.is_selected == '1'
        assert aid.page_time > 0
        if aid.score == 0:
            assert 'B' not in aid.response_value
        else:
            assert aid.score == 2
            assert aid.response_value == 'B,F'


def test_generate_response_for_sa():
    item = AssessmentItem()
    item.type = 'SA'
    item.max_score = 2
    item.difficulty = 2

    for _ in range(0, 100):
        aid = item_lvl_data.AssessmentOutcomeItemData()
        generate_response(aid, item)

        assert aid.is_selected == '1'
        assert aid.page_time > 1000
        assert len(aid.response_value) > 40
        assert aid.score in (0, 2)


def test_generate_response_for_wer():
    item = AssessmentItem()
    item.type = 'WER'
    item.max_score = 6
    item.difficulty = 2

    for _ in range(0, 100):
        aid = item_lvl_data.AssessmentOutcomeItemData()
        generate_response(aid, item)

        assert aid.is_selected == '1'
        assert aid.page_time > 1000
        assert len(aid.response_value) > 80
        assert aid.score in (0, 1, 2, 3, 4, 5, 6)
        assert len(aid.sub_scores) == 3


def test_generate_response_for_other():
    item = AssessmentItem()
    item.type = 'EQ'
    item.max_score = 1
    item.difficulty = 2

    aid = item_lvl_data.AssessmentOutcomeItemData()
    generate_response(aid, item)

    assert aid.is_selected == '1'
    assert aid.page_time > 1000
    if aid.score == 0:
        assert 'good' not in aid.response_value
    else:
        assert aid.score == 1
        assert 'good' in aid.response_value


def test_generate_response_low_capability():
    item = AssessmentItem()
    item.type = 'EQ'
    item.max_score = 1
    item.difficulty = 2

    total = 0
    for _ in range(0, 100):
        aid = item_lvl_data.AssessmentOutcomeItemData()
        generate_response(aid, item, 0.0)
        total += aid.score
    assert total < 50


def test_generate_response_high_capability():
    item = AssessmentItem()
    item.type = 'EQ'
    item.max_score = 1
    item.difficulty = 2

    total = 0
    for _ in range(0, 100):
        aid = item_lvl_data.AssessmentOutcomeItemData()
        generate_response(aid, item, 4.0)
        total += aid.score
    assert total > 50


# Helper to replace removed method
def __create_assessment_outcome_objects(student, asmt_summ, interim_asmts, id_gen, assessment_results, skip_rate,
                                        retake_rate, delete_rate, update_rate):
    # Create the summative assessment outcome
    asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt_summ, id_gen,
                                              assessment_results, skip_rate, retake_rate, delete_rate,
                                              update_rate, False)

    # Generate interim assessment results (list will be empty if school does not perform
    # interim assessments)
    for asmt in interim_asmts:
        # Create the interim assessment outcome
        asmt_gen.create_assessment_outcome_object(datetime.date(2015, 5, 15), student, asmt, id_gen,
                                                  assessment_results, skip_rate, retake_rate, delete_rate,
                                                  update_rate, False)
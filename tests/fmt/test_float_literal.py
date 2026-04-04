from spud_fmt import FmtConfig
from tests.fmt.helpers import bind, binop, float_, fmt, num


class TestFloatDefault:
    def test_standard_float(self):
        assert fmt().format_node(float_(3.14), 0) == "3.14"

    def test_zero_point_five_normalized(self):
        assert fmt().format_node(float_(0.5), 0) == "0.5"

    def test_trailing_dot_normalized_to_point_zero(self):
        assert fmt().format_node(float_(3.0), 0) == "3.0"

    def test_leading_dot_normalized_to_zero_point(self):
        assert fmt().format_node(float_(0.25), 0) == "0.25"

    def test_zero_point_zero(self):
        assert fmt().format_node(float_(0.0), 0) == "0.0"

    def test_large_float(self):
        assert fmt().format_node(float_(9999.9999), 0) == "9999.9999"


class TestFloatNormalizeLeadingZeroFalse:
    def test_point_five_keeps_leading_dot(self):
        cfg = FmtConfig(normalize_leading_zero=False)
        assert fmt(cfg).format_node(float_(0.5), 0) == ".5"

    def test_point_two_five_keeps_leading_dot(self):
        cfg = FmtConfig(normalize_leading_zero=False)
        assert fmt(cfg).format_node(float_(0.25), 0) == ".25"

    def test_standard_float_unaffected(self):
        cfg = FmtConfig(normalize_leading_zero=False)
        assert fmt(cfg).format_node(float_(3.14), 0) == "3.14"

    def test_trailing_zero_still_normalized(self):
        cfg = FmtConfig(normalize_leading_zero=False)
        assert fmt(cfg).format_node(float_(3.0), 0) == "3.0"

    def test_zero_point_zero_keeps_leading_dot(self):
        cfg = FmtConfig(normalize_leading_zero=False)
        assert fmt(cfg).format_node(float_(0.0), 0) == ".0"


class TestFloatNormalizeTrailingZeroFalse:
    def test_trailing_dot_restored(self):
        cfg = FmtConfig(normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(3.0), 0) == "3."

    def test_five_point_zero_trailing_dot_restored(self):
        cfg = FmtConfig(normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(5.0), 0) == "5."

    def test_standard_float_unaffected(self):
        cfg = FmtConfig(normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(3.14), 0) == "3.14"

    def test_leading_zero_still_normalized(self):
        cfg = FmtConfig(normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(0.5), 0) == "0.5"

    def test_zero_point_zero_trailing_dot_restored(self):
        cfg = FmtConfig(normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(0.0), 0) == "0."


class TestFloatBothNormalizationsDisabled:
    def test_zero_point_zero_both_dots(self):
        cfg = FmtConfig(normalize_leading_zero=False, normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(0.0), 0) == "."

    def test_leading_dot_no_trailing(self):
        cfg = FmtConfig(normalize_leading_zero=False, normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(0.5), 0) == ".5"

    def test_trailing_dot_no_leading(self):
        cfg = FmtConfig(normalize_leading_zero=False, normalize_trailing_zero=False)
        assert fmt(cfg).format_node(float_(3.0), 0) == "3."


class TestFloatInContext:
    def test_float_in_binding(self):
        assert fmt().format_node(bind("x", float_(3.14)), 0) == "x: Int := 3.14"

    def test_float_in_binary_op(self):
        assert fmt().format_node(binop(float_(1.5), "+", num(2)), 0) == "1.5 + 2"

    def test_float_in_binary_op_both_sides(self):
        assert fmt().format_node(binop(float_(1.1), "*", float_(2.2)), 0) == "1.1 * 2.2"

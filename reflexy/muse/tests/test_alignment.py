import pytest
from reflexy.muse.alignment import find_matches
import numpy as np

@pytest.fixture
def star_positions():
    np.random.seed(2508)
    x_ref = np.random.uniform(0, 100, 20)
    y_ref = np.random.uniform(0, 100, 20)


    return x_ref, y_ref

@pytest.fixture()
def offsets():
    np.random.seed(2508)
    x_offset = np.random.normal(0.5, 0.1, 20)
    y_offset = np.random.normal(0.5, 0.1, 20)

    return x_offset, y_offset


def test_find_matches(star_positions, offsets):
    x_ref, y_ref = star_positions
    x_offset, y_offset = offsets

    x_new = x_ref + x_offset
    y_new = y_ref + y_offset
    id = np.arange(20)

    m_x_offset, m_y_offset, n_matches, rms_x_offset, rms_y_offset = find_matches(
        id, x_ref, y_ref, id, x_new, y_new, 1.5)

    assert np.isclose(m_x_offset, -0.5, 1e-1)
    assert np.isclose(m_y_offset, -0.5, 1e-1)
    assert n_matches == 20
    assert np.isclose(rms_x_offset, 0.1, atol=0.1)
    assert np.isclose(rms_y_offset, 0.1, atol=0.1)



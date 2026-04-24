"""Tests for Phoenix-Bad API client."""
import pytest
from custom_components.phoenix_bad.api import PhoenixBadApiClient, PhoenixBadParseError
from unittest.mock import MagicMock

def test_parse_response_success():
    """Test successful parsing of HTML response."""
    html = '<div class="outer_wrapper" data-free="10"><div class="inner_wrapper" style="width: 50.0%;"></div></div>'
    client = PhoenixBadApiClient()
    data = client._parse_response(html, "Pool")
    
    assert data.free == 10
    assert data.occupied == 10 # 50% of 20 total (10 free, 10 occupied)
    assert data.percentage == 50.0

def test_parse_response_area_missing():
    """Test parsing when area data is missing."""
    html = "Area data missing..."
    client = PhoenixBadApiClient()
    data = client._parse_response(html, "Pool")
    
    assert data.free == 0
    assert data.occupied == 0
    assert data.percentage == 0.0

def test_parse_response_fallback_selectors():
    """Test fallback selectors when classes are missing."""
    html = '<div data-free="20"><div style="width: 25%;"></div></div>'
    client = PhoenixBadApiClient()
    data = client._parse_response(html, "Pool")
    
    assert data.free == 20
    assert data.percentage == 25.0
    # occupied = (25 * 20) / (100 - 25) = 500 / 75 = 6.66 -> 7
    assert data.occupied == 7

def test_parse_response_invalid_html():
    """Test parsing with invalid HTML."""
    html = '<div>No data here</div>'
    client = PhoenixBadApiClient()
    with pytest.raises(PhoenixBadParseError):
        client._parse_response(html, "Pool")

def test_parse_response_100_percent():
    """Test 100% occupancy edge case."""
    html = '<div class="outer_wrapper" data-free="5"><div class="inner_wrapper" style="width: 100%;"></div></div>'
    client = PhoenixBadApiClient()
    data = client._parse_response(html, "Pool")
    
    assert data.percentage == 100.0
    assert data.occupied == 5 # Based on assume total = 2 * free in api.py

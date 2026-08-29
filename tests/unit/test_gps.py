"""Unit tests for GPS extraction and reverse geocoding."""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

from photorg.core.exif import _dms_to_decimal


class TestGPSConversion:
    """Tests for DMS to decimal conversion."""

    def test_dms_to_decimal_north_east(self) -> None:
        """Standard N/E coordinates should be positive."""
        dms = (48.0, 51.0, 30.0)  # Eiffel Tower approx (48°51'30"N)
        assert _dms_to_decimal(dms, 'N') == pytest.approx(48.85833, 0.0001)

    def test_dms_to_decimal_south_west(self) -> None:
        """S/W coordinates should be negative."""
        dms = (22.0, 58.0, 14.0)  # Christ the Redeemer approx (22°58'14"S)
        assert _dms_to_decimal(dms, 'S') == pytest.approx(-22.97055, 0.0001)

        dms_w = (43.0, 12.0, 43.0) # Christ the Redeemer approx (43°12'43"W)
        assert _dms_to_decimal(dms_w, 'W') == pytest.approx(-43.21194, 0.0001)

    def test_invalid_dms(self) -> None:
        """Invalid inputs should safely return None."""
        assert _dms_to_decimal((1,), 'N') is None
        assert _dms_to_decimal(("bad", 1, 1), 'N') is None
        assert _dms_to_decimal(None, 'N') is None


class TestReverseGeocode:
    """Tests for reverse geocoding via Nominatim."""

    @patch("photorg.core.geocoder.urllib.request.urlopen")
    def test_reverse_geocode_success(self, mock_urlopen) -> None:
        """Successful API response should return the best location name."""
        from photorg.core.geocoder import reverse_geocode

        # Reset cache for testing
        reverse_geocode.cache_clear()

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"address": {"tourism": "Eiffel Tower", "city": "Paris"}}'
        # __enter__ is for the context manager ('with' block)
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Call with dummy coordinates
        result = reverse_geocode(48.8584, 2.2945)
        
        assert result == "Eiffel Tower"
        mock_urlopen.assert_called_once()

    @patch("photorg.core.geocoder.urllib.request.urlopen")
    def test_reverse_geocode_fallback_to_city(self, mock_urlopen) -> None:
        """If no famous spot is found, fall back to the city/town name."""
        from photorg.core.geocoder import reverse_geocode

        reverse_geocode.cache_clear()

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"address": {"city": "Berlin", "country": "Germany"}}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = reverse_geocode(52.5200, 13.4050)
        
        assert result == "Berlin"

    @patch("photorg.core.geocoder.urllib.request.urlopen")
    def test_reverse_geocode_error(self, mock_urlopen) -> None:
        """API errors (e.g. timeout, 404, no internet) should return None."""
        from photorg.core.geocoder import reverse_geocode
        import urllib.error

        reverse_geocode.cache_clear()

        # Simulate network error
        mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")

        result = reverse_geocode(0.0, 0.0)
        assert result is None

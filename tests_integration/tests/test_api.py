"""Integration tests for the API."""

import httpx

URL = "http://spoolman:8000"


def test_add_vendor():
    """Test adding a vendor to the database."""
    # Execute
    name = "John"
    comment = "abcdefghåäö"
    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": name, "comment": comment},
    )
    result.raise_for_status()

    # Verify
    vendor = result.json()
    assert vendor["name"] == name
    assert vendor["comment"] == comment
    assert vendor["id"] is not None
    assert vendor["registered"] is not None

    # Clean up
    httpx.delete(f"{URL}/api/v1/vendor/{vendor['id']}").raise_for_status()


def test_get_vendor():
    """Test getting a vendor from the database."""
    # Setup
    name = "John"
    comment = "abcdefghåäö"
    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": name, "comment": comment},
    )
    result.raise_for_status()
    added_vendor = result.json()

    # Execute
    result = httpx.get(
        f"{URL}/api/v1/vendor/{added_vendor['id']}",
    )
    result.raise_for_status()

    # Verify
    vendor = result.json()
    assert vendor["name"] == name
    assert vendor["comment"] == comment
    assert vendor["id"] == added_vendor["id"]
    assert vendor["registered"] == added_vendor["registered"]

    # Clean up
    httpx.delete(f"{URL}/api/v1/vendor/{vendor['id']}").raise_for_status()


def test_find_vendors():
    """Test finding vendors from the database."""
    # Setup
    name_1 = "John"
    comment_1 = "abcdefghåäö"
    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": name_1, "comment": comment_1},
    )
    result.raise_for_status()
    vendor_1 = result.json()

    name_2 = "Stan"
    comment_2 = "gfdadfg"
    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": name_2, "comment": comment_2},
    )
    result.raise_for_status()
    vendor_2 = result.json()

    added_vendors_by_id = {
        vendor_1["id"]: vendor_1,
        vendor_2["id"]: vendor_2,
    }

    # Execute - Find all vendors
    result = httpx.get(
        f"{URL}/api/v1/vendor",
    )
    result.raise_for_status()

    # Verify
    vendors = result.json()
    assert len(vendors) == 2

    for vendor in vendors:
        added_vendor = added_vendors_by_id[vendor["id"]]
        assert vendor["name"] == added_vendor["name"]
        assert vendor["comment"] == added_vendor["comment"]
        assert vendor["id"] == added_vendor["id"]
        assert vendor["registered"] == added_vendor["registered"]

    # Execute - Find a specific vendor
    result = httpx.get(
        f"{URL}/api/v1/vendor",
        params={"name": name_1},
    )
    result.raise_for_status()

    # Verify
    vendors = result.json()
    assert len(vendors) == 1

    vendor = vendors[0]

    assert vendor["name"] == name_1
    assert vendor["comment"] == comment_1
    assert vendor["id"] == vendor_1["id"]
    assert vendor["registered"] == vendor_1["registered"]

    # Clean up
    httpx.delete(f"{URL}/api/v1/vendor/{vendor_1['id']}").raise_for_status()
    httpx.delete(f"{URL}/api/v1/vendor/{vendor_2['id']}").raise_for_status()


def test_delete_vendor():
    """Test deleting a vendor from the database."""
    # Setup
    name = "John"
    comment = "abcdefghåäö"
    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": name, "comment": comment},
    )
    result.raise_for_status()
    added_vendor = result.json()

    # Execute
    httpx.delete(
        f"{URL}/api/v1/vendor/{added_vendor['id']}",
    ).raise_for_status()

    # Verify
    result = httpx.get(
        f"{URL}/api/v1/vendor/{added_vendor['id']}",
    )
    assert result.status_code == 404


def test_update_vendor():
    """Test update a vendor in the database."""
    # Setup
    name = "John"
    comment = "abcdefghåäö"
    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": name, "comment": comment},
    )
    result.raise_for_status()
    added_vendor = result.json()

    # Execute
    new_name = "Stan"
    new_comment = "gfdadfg"
    result = httpx.patch(
        f"{URL}/api/v1/vendor/{added_vendor['id']}",
        json={"name": new_name, "comment": new_comment},
    )
    result.raise_for_status()

    # Verify
    vendor = result.json()
    assert vendor["name"] == new_name
    assert vendor["comment"] == new_comment
    assert vendor["id"] == added_vendor["id"]
    assert vendor["registered"] == added_vendor["registered"]

    # Clean up
    httpx.delete(f"{URL}/api/v1/vendor/{vendor['id']}").raise_for_status()

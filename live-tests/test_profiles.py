"""test_profiles.py

Tests for the Synack Profiles APIs

=== NOTE ===
ALL potentially sensitive variables here is FAKE, and NOT real API data!
Values SHOULD represent exactly what real data would look like.
Types MUST represent the exact types of real data.
"""

import sys
import os
import pprint
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


profile = {
    "acropolis_handle": [None, "somehacker"],
    "address_country": ["US"],
    "admission_step_completed": ["requested_admission_package"],
    "all_certifications": [["Cert", "Other Cert"]],
    "bitcoin_address": [None, "wfaglu"],
    "city": ["Some City"],
    "claim_limit": [500.0],
    "country": ["US"],
    "created_at": [1601674526],
    "display_name": ["somehacker"],
    "email": ["some@hacker.io"],
    "facebook_handle": [None, "somehacker"],
    "federal_eligible": [True],
    "first_name": ["JOE"],
    "github_handle": [None, "somehacker"],
    "has_hyperwallet_user_creation_data": [True],
    "hyperwallet_domain": ["api.paylution.com"],
    "hyperwallet_user_token": ["usr-a4f46cec-f265-4203-bdf3-96e7a2487fb1"],
    "last_name": ["SCHMOE"],
    "last_sign_in_at": ["2022-01-29 22:17:13 UTC"],
    "linked_in_handle": [None, "somehacker"],
    "me": [True],
    "notification_preferences": [
        {
            "blitz:began": 0,
            "bonus:awarded": 1
        }
    ],
    "opt_in_leaderboard": [True],
    "paypal_email": ["some@hacker.com"],
    "phone": ['1235550123'],
    "postal_code": ["12345"],
    "slug": ["somehacker"],
    "spotify_handle": [None, "somehacker"],
    "state_province": ["SomeState"],
    "street_1": ["123 Main St."],
    "street_2": [""],
    "synack_employee": [False],
    "tax_form_signed_at": [1601694528],
    "terms_signed_at": [1601724264],
    "tier": [5],
    "twitter_handle": [None, "somehacker"],
    "url": [""],
    "user_id": ["lupmgfpu"],
    "workspace": [{
        "id": [123],
        "os": ["linux"],
        "region": ["us-east4-a"],
        "researcher_profile_id": [462],
        "status": ["assigned"],
        "updated_at": ["2021-12-07T01:18:34Z"],
        "workspace_id": [None]
    }],
    "workspace_access": [True],
    "workspace_connected": [True],
    "workspace_created_at": [0],
    "workspace_terms_signed_at": [1618461248],
    "workspace_user_info_updated_at": [0],
    "workspace_username": ["SRT_lupmgfpu"],
    "zendesk_subdomain": ["synack.zendesk.com"],
    "zendesk_widget_token": ["j.w.t"]
}


class ProfileTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ans = input("These tests run against the live Synack API " +
                    "to easily identify changes.\n" +
                    "If you are sure you intend to run these, enter 'yes': ")
        if ans != 'yes' and ans != 'y':
            exit()
        cls.h = synack.Handler()

    def test_profile_parameters(self):
        """Should have the same profile parameters"""
        ret = self.h.users.get_profile()
        pp = pprint.pformat(ret)
        for k in ret.keys():
            types = [type(v) for v in profile[k]]
            err = f"{k} : Real={ret[k]} : Mock={profile[k]}"
            self.assertTrue(type(ret[k]) in types, err)

        prop_count = len(profile.keys())
        self.assertEqual(prop_count, len(ret.keys()), pp)

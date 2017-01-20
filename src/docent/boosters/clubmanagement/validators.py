from collections import Counter, defaultdict
from zope.interface import Invalid
from z3c.form import validator

class BoosterClubValidators(validator.InvariantsValidator):
    def validateClubOfficers(self, obj):
        errors = super(BoosterClubValidators, self).validateClubOfficers(obj)
        club_officer_dict = {}
        club_officer_reverse_lookup_dict = defaultdict(list)
        officer_counter = Counter()
        club_officer_dict['club_president'] = obj.club_president
        club_officer_dict['club_secretary'] = obj.club_secretary
        club_officer_dict['club_treasurer'] = obj.club_treasurer
        club_officer_dict['club_advisor'] = obj.club_advisor
        #[ club_officer_reverse_lookup_dict[club_officer_dict[key]].append(key) for key in club_officer_dict ]
        [ officer_counter.update(club_officer_dict[key]) for key in club_officer_dict ]

        for member_key in officer_counter:
            if officer_counter[member_key] > 2:
                errors += (Invalid('%s can only serve in two officer positions' % member_key),)

        return errors

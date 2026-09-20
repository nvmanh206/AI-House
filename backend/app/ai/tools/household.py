def get_household_profile(service):
    profile=service.profile()
    return {k:profile[k] for k in ('id','member_count')}

def get_household_profile(service, *args, **kwargs):
    profile=service.profile()
    return {k:profile[k] for k in ('id','member_count')}

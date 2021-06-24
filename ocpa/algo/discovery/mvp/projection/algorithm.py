from ocpa.algo.discovery.mvp.projection.versions import classic, activity_occurrence,group_size_hist

CLASSIC = "classic"
ACTIVITY_OCCURRENCE = "activity_occurrence"
GROUP_SIZE_HIST = "group_size_hist"

VERSIONS = {CLASSIC: classic.apply, ACTIVITY_OCCURRENCE: activity_occurrence.apply, GROUP_SIZE_HIST: group_size_hist.apply}


def apply(df, persp, variant=CLASSIC, parameters=None):
    return VERSIONS[variant](df, persp, parameters=parameters)

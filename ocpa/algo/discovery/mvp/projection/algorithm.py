from ocpa.algo.discovery.mvp.projection.versions import classic, activity_occurrence, object_count

CLASSIC = "classic"
ACTIVITY_OCCURRENCE = "activity_occurrence"
OBJECT_COUNT = "object_count"

VERSIONS = {CLASSIC: classic.apply, ACTIVITY_OCCURRENCE: activity_occurrence.apply,
            OBJECT_COUNT: object_count.apply}


def apply(df, persp, variant=CLASSIC, parameters=None):
    return VERSIONS[variant](df, persp, parameters=parameters)

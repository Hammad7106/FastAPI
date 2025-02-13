import sentry_sdk

sentry_sdk.init(
    dsn="https://9c993af516b43e8b3a89cfcc34f2af33@o4508809919987712.ingest.us.sentry.io/4508809922805760",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

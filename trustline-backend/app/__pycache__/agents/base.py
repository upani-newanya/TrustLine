class Agent:
    """Simple base class for agents in the pipeline."""

    def process(self, *args, **kwargs):
        raise NotImplementedError()

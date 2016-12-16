import os
import warnings

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DEBUG = False

from nengo_deeplearning.builder import Builder  # noqa: F401
from nengo_deeplearning.simulator import Simulator  # noqa: F401

# need to explicitly import these to trigger the builder registration
from nengo_deeplearning import (  # noqa: F401
    operators, neurons, processes, learning_rules)

# --- check version
import nengo

minimum_nengo_version = (2, 3, 0)
latest_nengo_version = (2, 3, 0)
if nengo.version.version_info < minimum_nengo_version:
    raise ValueError(
        "`nengo_deeplearning` does not support `nengo` version %s. Upgrade "
        "with 'pip install --upgrade --no-deps nengo'."
        % nengo.__version__)
elif nengo.version.version_info > latest_nengo_version:
    warnings.warn("This version of `nengo_deeplearning` has not been tested "
                  "with your `nengo` version (%s). The latest fully "
                  "supported version is %s" % (
                      nengo.__version__, latest_nengo_version))

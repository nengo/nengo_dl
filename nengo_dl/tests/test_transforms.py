# pylint: disable=missing-docstring

from distutils.version import LooseVersion

import nengo
from nengo.exceptions import ValidationError
import numpy as np
import pytest

from nengo_dl.utils import tf_gpu_installed


@pytest.mark.skipif(LooseVersion(nengo.__version__) <= "2.8.0",
                    reason="Nengo Convolutions not implemented")
@pytest.mark.parametrize("channels_last", (True, False))
def test_merge_conv(Simulator, channels_last, seed, pytestconfig):
    from nengo.builder.transforms import ConvInc

    with nengo.Network(seed=seed) as net:
        a = nengo.Node(np.ones(32))
        b = nengo.Node(size_in=12)
        c = nengo.Node(size_in=12)
        nengo.Connection(a, b, synapse=None, transform=nengo.Convolution(
            3, (4, 4, 2) if channels_last else (2, 4, 4),
            channels_last=channels_last))
        nengo.Connection(a, c, synapse=None, transform=nengo.Convolution(
            3, (4, 4, 2) if channels_last else (2, 4, 4),
            channels_last=channels_last))
        p_b = nengo.Probe(b)
        p_c = nengo.Probe(c)

    with pytest.warns(None) as recwarns:
        with Simulator(net) as sim:
            assert len([ops for ops in sim.tensor_graph.plan
                        if isinstance(ops[0], ConvInc)]) == 1

            sim.step()

    # check for warning about force_last
    # note: this also assures us that we are testing on the GPU in native
    # channels_first when possible
    recwarns = [w for w in recwarns if "channels_last=False" in str(w.message)]
    if channels_last or (tf_gpu_installed
                         and pytestconfig.getoption("--device") != "/cpu:0"):
        assert len(recwarns) == 0
    else:
        assert len(recwarns) == 1

    with nengo.Simulator(net) as canonical:
        canonical.step()

    assert np.allclose(sim.data[p_b], canonical.data[p_b])
    assert np.allclose(sim.data[p_c], canonical.data[p_c])


@pytest.mark.skipif(LooseVersion(nengo.__version__) <= "2.8.0",
                    reason="Nengo Convolutions not implemented")
@pytest.mark.parametrize("d", (3, 4))
def test_conv_error(Simulator, d):
    with nengo.Network() as net:
        a = nengo.Node([0])
        b = nengo.Node(size_in=1)
        nengo.Connection(a, b, transform=nengo.Convolution(
            1, [1] * (d + 1), kernel_size=[1] * d, strides=[1] * d))

    try:
        with Simulator(net):
            pass
    except NotImplementedError:
        assert d == 4
    else:
        assert d == 3


@pytest.mark.skipif(LooseVersion(nengo.__version__) <= "2.8.0",
                    reason="Nengo Convolutions not implemented")
@pytest.mark.parametrize("dimensions", (1, 2))
@pytest.mark.parametrize("padding", ("same", "valid"))
@pytest.mark.parametrize("channels_last", (True, False))
@pytest.mark.parametrize("fixed_kernel", (True, False))
def test_convolution(
        dimensions,
        padding,
        channels_last,
        fixed_kernel,
        Simulator,
        rng,
        seed):
    # This test is a copy of nengo/tests/test_transforms.py::test_convolution
    # with only the `allclose` tolerance modified.
    from nengo._vendor.npconv2d import conv2d

    input_d = 4
    input_channels = 2
    output_channels = 5
    kernel_d = 3
    kernel_size = (kernel_d,) if dimensions == 1 else (kernel_d, kernel_d)
    output_d = input_d - kernel_d // 2 * 2 if padding == "valid" else input_d

    input_shape = (input_d, input_channels)
    kernel_shape = (kernel_d, input_channels, output_channels)
    output_shape = (output_d, output_channels)

    if dimensions == 2:
        input_shape = (input_d,) + input_shape
        kernel_shape = (kernel_d,) + kernel_shape
        output_shape = (output_d,) + output_shape

    if not channels_last:
        input_shape = tuple(np.roll(input_shape, 1))
        output_shape = tuple(np.roll(output_shape, 1))

    with nengo.Network(seed=seed) as net:
        x = rng.randn(*input_shape)
        w = (rng.randn(*kernel_shape) if fixed_kernel
             else nengo.dists.Uniform(-0.1, 0.1))

        a = nengo.Node(np.ravel(x))
        b = nengo.Node(size_in=np.prod(output_shape))
        conn = nengo.Connection(
            a, b,
            synapse=None,
            transform=nengo.Convolution(
                output_channels,
                input_shape,
                init=w,
                padding=padding,
                kernel_size=kernel_size,
                strides=(1,) if dimensions == 1 else (1, 1),
                channels_last=channels_last))
        p = nengo.Probe(b)

        # check error handling
        bad_in = nengo.Node([0])
        bad_out = nengo.Node(size_in=5)
        with pytest.raises(ValidationError):
            nengo.Connection(bad_in, b, transform=conn.transform)
        with pytest.raises(ValidationError):
            nengo.Connection(a, bad_out, transform=conn.transform)

    assert conn.transform.output_shape.shape == output_shape
    assert conn.transform.kernel_shape == kernel_shape

    with Simulator(net) as sim:
        sim.step()

    weights = sim.data[conn].weights
    if not channels_last:
        x = np.moveaxis(x, 0, -1)
    if dimensions == 1:
        x = x[:, None, :]
        weights = weights[:, None, :, :]
    truth = conv2d.conv2d(x[None, ...], weights, pad=padding.upper())[0]
    if not channels_last:
        truth = np.moveaxis(truth, -1, 0)

    assert np.allclose(sim.data[p][0], np.ravel(truth), atol=1e-6)
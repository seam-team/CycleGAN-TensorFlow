import tensorflow as tf
import ops

class Generator:
  def __init__(self, name, is_training, fake_buffer_size=50, image_size=128):
    self.name = name
    self.reuse = False
    self.is_training = is_training

    # TODO: store the newest generated images
    # self.buffer = tf.get_variable('fake_buffer_' + name,
    #     shape=[fake_buffer_size, image_size, image_size, 3],
    #     initializer=tf.constant_initializer(0.0),
    #     trainable=False)

  def __call__(self, input):
    """
    Args:
      input: batch_size x 128 x 128 x 3
    Returns:
      output: same size as input
    """
    with tf.variable_scope(self.name):
      # conv layers
      c7s1_32 = ops.c7s1_k(input, 32, is_training=self.is_training,
          reuse=self.reuse, name='c7s1_32')                             # (?, 128, 128, 32)
      d64 = ops.dk(c7s1_32, 64, is_training=self.is_training,
          reuse=self.reuse, name='d64')                                 # (?, 64, 64, 64)
      d128 = ops.dk(d64, 128, is_training=self.is_training,
          reuse=self.reuse, name='d128')                                # (?, 32, 32, 128)

      # 6 residual blocks
      R128_1 = ops.Rk(d128, 128, reuse=self.reuse, name='R128_1')       # (?, 32, 32, 128)
      R128_2 = ops.Rk(R128_1, 128, reuse=self.reuse, name='R128_2')     # (?, 32, 32, 128)
      R128_3 = ops.Rk(R128_2, 128, reuse=self.reuse, name='R128_3')     # (?, 32, 32, 128)
      R128_4 = ops.Rk(R128_3, 128, reuse=self.reuse, name='R128_4')     # (?, 32, 32, 128)
      R128_5 = ops.Rk(R128_4, 128, reuse=self.reuse, name='R128_5')     # (?, 32, 32, 128)
      R128_6 = ops.Rk(R128_5, 128, reuse=self.reuse, name='R128_6')     # (?, 32, 32, 128)

      # fractional-strided convolution
      u64 = ops.uk(R128_6, 64, is_training=self.is_training,
          reuse=self.reuse, name='u64')                                 # (?, 64, 64, 64)
      u32 = ops.uk(u64, 32, is_training=self.is_training,
          reuse=self.reuse, name='u32')                                 # (?, 128, 128, 32)

      # conv layer
      # Note: the paper said that ReLU and batch_norm were used
      # but actually tanh was used and no batch_norm here
      output = ops.c7s1_k(u32, 3, batch_norm=False,
          activation='tanh', reuse=self.reuse, name='output')           # (?, 128, 128, 3)
    # set reuse=True for next call
    self.reuse = True
    self.variables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    return output



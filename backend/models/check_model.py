import tensorflow as tf

model = tf.keras.models.load_model('c:/Users/cloep/0Code/DL/tennis/backend/models/tennis_model.keras')
print('Input shape:', model.input_shape)

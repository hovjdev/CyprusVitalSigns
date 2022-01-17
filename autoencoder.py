import os
import math
import random
import json
import glob
import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import Sequence
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, Flatten, Dense, UpSampling2D, Reshape
import tensorflow_probability as tfp

from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

DATA_DIRS = []

WORKDIR='../output/autoencoder'

DATA_DIRS = [f'{WORKDIR}/images']
OUTPUT_DIR = f'{WORKDIR}'
os.system(f'mkdir -p "{OUTPUT_DIR}"')

tfd = tfp.distributions
tfpl = tfp.layers
tfb = tfp.bijectors


def get_image_filelist(data_dirs=[]):
    filelist=[]
    for d in DATA_DIRS:
        l = glob.glob(f'{d}/*.png')
        filelist.extend(l)
    print(f"Found {len(filelist)} images.")
    return filelist


def prep_images(filelist):
    output_filelist=[]
    output = os.path.join(OUTPUT_DIR, 'images')
    os.system(f'mkdir -p {output}')
    default_img=None
    i=0
    for f in filelist:
        with Image.open(f) as img:
            try:
                img = Image.open(f)
                img = img.convert('RGB')
            except:
                img = default_img

            if default_img is None:
                default_img = img

            if True:
            #try:
                left = int(img.size[0]/2)-64
                top = int(img.size[1]/2)-64
                img2 = img.crop((left, top, left+128, top+128))
                i=i+1
                image_path =os.path.join(output, f'im{i}.png')
                img2.save(image_path, format="PNG")
                output_filelist.append(image_path)
            #except:
            #    pass
    return output_filelist



class ImageGenerator(Sequence):
    # initialize the custom generator
    def __init__(self, filelist, batch_size, target_height, target_width):
        self.filelist = filelist
        self.batch_size = batch_size
        self.target_height = target_height
        self.target_width = target_width
        self.default_img = None

    # shuffle the data after each epoch
    def on_epoch_end(self):
        random.shuffle(self.filelist)


    # select a batch as tensor
    def __getitem__(self, index):
        cur_files = self.filelist[index*self.batch_size:(index+1)*self.batch_size]
        X, y = self.__data_generation(cur_files)
        return X, y

    #
    def __data_generation(self, cur_files):
        # initialize empty tensors to store the images
        X = np.empty(shape=(self.batch_size, self.target_height, self.target_width, 3))
        Y = np.empty(shape=(self.batch_size, self.target_height, self.target_width, 3))

        # loop through the current batch and build the tensors
        for i in range(0, self.batch_size):
            # read image
            img_uri = cur_files[i]
            #print(img_uri)

            img=None
            try:
                with Image.open(img_uri) as img:
                    img = Image.open(img_uri)
                    img = img.convert('RGB')
            except:
                img = self.default_img

            if self.default_img is None:
                self.default_img = img.copy()

            # resize image
            if img.size[0] != self.target_width or img.size[1] != self.target_height:
                img = img.resize((self.target_width, self.target_height), Image.ANTIALIAS)
            # store image in tensors
            img = np.array(img).astype(np.float32) / 255.
            X[i] = img
            Y[i] = img

        return X, Y

    # get number of batches
    def __len__(self):
        return int(np.floor(len(self.filelist) / self.batch_size))



def get_prior(num_modes, latent_dim):
    prior = tfd.MixtureSameFamily(
        mixture_distribution=tfd.Categorical(probs=[1 / num_modes,] * num_modes),
        components_distribution=tfd.MultivariateNormalDiag(
            loc=tf.Variable(tf.random.normal(shape=[num_modes, latent_dim])),
            scale_diag=tfp.util.TransformedVariable(tf.Variable(tf.ones(shape=[num_modes, latent_dim])), bijector=tfb.Softplus())
        )
    )
    return prior

def get_kl_regularizer(prior_distribution):
    divergence_regularizer = tfpl.KLDivergenceRegularizer(
        prior_distribution,
        use_exact_kl=False,
        weight=1.0,
        test_points_fn=lambda q: q.sample(3),
        test_points_reduce_axis=(0, 1)
    )
    return divergence_regularizer

def get_encoder(latent_dim, kl_regularizer):
    encoder = Sequential([
        Conv2D(32, (4, 4), activation='relu', strides=2, padding='SAME', input_shape=(128, 128, 3)),
        BatchNormalization(),
        Conv2D(64, (4, 4), activation='relu', strides=2, padding='SAME'),
        BatchNormalization(),
        Conv2D(128, (4, 4), activation='relu', strides=2, padding='SAME'),
        BatchNormalization(),
        Conv2D(256, (4, 4), activation='relu', strides=2, padding='SAME'),
        BatchNormalization(),
        Conv2D(512, (4, 4), activation='relu', strides=2, padding='SAME'),
        BatchNormalization(),
        Flatten(),
        Dense(tfpl.MultivariateNormalTriL.params_size(latent_dim)),
        tfpl.MultivariateNormalTriL(latent_dim, activity_regularizer=kl_regularizer)
    ])
    return encoder

def get_decoder(latent_dim):
    decoder = Sequential([
        Dense(8192, activation='relu', input_shape=(latent_dim, )),
        Reshape((4, 4, 512)),
        UpSampling2D(size=(2, 2)),
        Conv2D(256, (3, 3), activation='relu', padding='SAME'),
        UpSampling2D(size=(2, 2)),
        Conv2D(128, (3, 3), activation='relu', padding='SAME'),
        UpSampling2D(size=(2, 2)),
        Conv2D(64, (3, 3), activation='relu', padding='SAME'),
        UpSampling2D(size=(2, 2)),
        Conv2D(32, (3, 3), activation='relu', padding='SAME'),
        UpSampling2D(size=(2, 2)),
        Conv2D(128, (3, 3), activation='relu', padding='SAME'),
        Conv2D(3, (3, 3), padding='SAME'),
        Flatten(),
        tfpl.IndependentBernoulli(event_shape=(128, 128, 3))
    ])
    return decoder

def reconstruction_loss(batch_of_images, decoding_dist):
    """
    The function takes batch_of_images (Tensor containing a batch of input images to
    the encoder) and decoding_dist (output distribution of decoder after passing the
    image batch through the encoder and decoder) as arguments.
    The function should return the scalar average expected reconstruction loss.
    """
    return -tf.reduce_mean(decoding_dist.log_prob(batch_of_images), axis=0)



def generate_images(prior, decoder, n_samples):
    """
    The function takes the prior distribution, decoder and number of samples as inputs, which
    should be used to generate the images.
    The function should then return the batch of generated images.
    """
    z = prior.sample(n_samples)
    return decoder(z).mean()


def save_model(model, file_root):
    # serialize model to JSON
    model_json = model.to_json()
    with open(file_root + '.json', "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    for i in range(len(model.weights)):
        model.weights[i]._handle_name = model.weights[i].name + "_" + str(i)
    model.save_weights(file_root + '.h5')
    print(f"Saved {file_root} to disk")


def get_input_samples(gen, nb):
    input_images=[]
    for im in gen:
        if len(input_images) >= nb:
            break
        input_images.append(im)

    input_images = np.array(input_images)
    input_images = np.reshape(input_images,  newshape=(-1, WIDTH, HEIGHT, 3))

    return input_images[:nb]

def load_weights(encoder, decoder, vae):
      decoder.load_weights(os.path.join(OUTPUT_DIR, 'decoder.h5'))
      encoder.load_weights(os.path.join(OUTPUT_DIR, 'encoder.h5'))
      vae.load_weights(os.path.join(OUTPUT_DIR, 'vae.h5'))



def plot_images(images, fname, show=True):
  nr = math.ceil(int(len(images)/10))
  f, axs = plt.subplots(nr, 10, figsize=(16, 1.6*math.ceil(len(images)/10)))

  for j in range(len(images)):
      r = int(j/10)
      c =  j % 10
      axs[r][c].imshow(images[j])
      axs[r][c].axis('off')

  plt.tight_layout()
  plt.subplots_adjust( wspace=0, hspace=0)
  plt.savefig(fname, format='png', dpi=600)
  if show:
      plt.show()
  plt.close('all')


filelist = get_image_filelist(data_dirs=DATA_DIRS)
#filelist = prep_images(filelist)



# hyperparameters
TRAIN=False
RELOAD=True
HEIGHT = 128
WIDTH = 128
BATCH_SIZE = 16
EPOCHS=30
LATENT_DIM=50
N_SAMPLES = 100



prior = get_prior(num_modes=2, latent_dim=LATENT_DIM)
kl_regularizer = get_kl_regularizer(prior)
encoder = get_encoder(latent_dim=LATENT_DIM, kl_regularizer=kl_regularizer)
encoder.summary()
decoder = get_decoder(latent_dim=LATENT_DIM)
decoder.summary()
vae = Model(inputs=encoder.inputs, outputs=decoder(encoder.outputs))

if RELOAD:
  load_weights(encoder, decoder, vae)



optimizer = tf.keras.optimizers.Adam(learning_rate=0.0005)
vae.compile(optimizer=optimizer, loss=reconstruction_loss)

# split images into training and validation sets
image_train, image_val =  train_test_split(filelist, test_size=0.1, random_state=101)

# create image generators for training
gen = ImageGenerator(image_train,  batch_size=BATCH_SIZE, target_height=HEIGHT, target_width=WIDTH)

# create image generators for validation
gen_val = ImageGenerator(image_val,  batch_size=BATCH_SIZE, target_height=HEIGHT, target_width=WIDTH)


if TRAIN:
    vae.fit(gen, validation_data=gen_val, epochs=EPOCHS)
    save_model(encoder, os.path.join(OUTPUT_DIR, 'encoder'))
    save_model(decoder, os.path.join(OUTPUT_DIR, 'decoder'))
    save_model(vae, os.path.join(OUTPUT_DIR, 'vae'))


load_weights(encoder, decoder, vae)

if True:
    # Generate samples
    input_samples = get_input_samples(gen=gen, nb=N_SAMPLES)
    plot_images(input_samples, os.path.join(OUTPUT_DIR, 'image_input.png'), show=False)

    sampled_images = generate_images(prior, decoder, N_SAMPLES)
    plot_images(sampled_images, os.path.join(OUTPUT_DIR, 'image_output.png'), show=False)


# Sort samples
nb=1000
input_samples = get_input_samples(gen=gen, nb=nb)
output_samples = decoder(encoder(input_samples).mean()).mean()
encoded = encoder(input_samples).mean()
print(encoded.shape)

pca = PCA(n_components=2)
y=pca.fit_transform(encoded)
print(y.shape)
y[:,0]=(y[:,0] - y[:,0].min()) / (y[:,0].max() - y[:,0].min())
y[:,1]=(y[:,1] - y[:,1].min()) / (y[:,1].max() - y[:,1].min())
neigh = NearestNeighbors(n_neighbors=20)
neigh.fit(y)
sorted_ims = []
for i in range(10):
    for j in range(10):
        n=neigh.kneighbors([[i/10.+0.05, j/10.+0.05]], return_distance=False)
        n=n.flatten()
        item=0
        for nn in n:
            if nn not in sorted_ims:
                item=nn
                break
        sorted_ims.append(item)

sorted_input = []
sorted_output = []
for item in sorted_ims:
    sorted_input.append(input_samples[item])
    sorted_output.append(output_samples[item])


plot_images(sorted_input, os.path.join(OUTPUT_DIR, f'image_sorted_input.png'), show=True)
plot_images(sorted_output, os.path.join(OUTPUT_DIR, f'image_sorted_output.png'), show=True)

#!/usr/bin/env python

import image_classify
import glob
import random

cat_images = glob.glob('cat/*.jpg')
assert(len(cat_images) > 10)

not_cat_images = glob.glob('not_cat/*.jpg')
assert(len(not_cat_images) > 10)

selected_not_cat_images = [ x for x in not_cat_images if os.path.getsize(x) > 80 * 1024 ]
selected_not_cat_images = random.sample(selected_not_cat_images, len(cat_images))

images = cat_images + selected_not_cat_images

assert(len(images) == 2 * len(cat_images))


c = image_classify.ImageClassify(['cat', 'not_cat'], image_size=100, learning_rate=0.001)
c.prepare_data(images)
c.train_model('cat_water')

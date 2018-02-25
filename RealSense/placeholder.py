from audio_module import audio_module as audio

# play audio according to data retrived from object detection
def playAudioFromBbox(bbox, dim=(416, 416)):
	x = bbox[2][0]
	label = bbox[0]
	if 0 <= x && x <= dim[0] / 3.0:
		audio.play(label, 'left')
	elif x <= dim[0] * 2 / 3.0:
		audio.play(label, 'front')
	else:
		audio.play(label, 'right')
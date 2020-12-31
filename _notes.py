# failed attempts

def detect_scale(self):
		"""
		On initialization, determine the best scale for template image
		to match the input image.
		"""

		# load the image image, convert it to grayscale, and detect edges
		template = cv2.imread('seed_9x9.png')
		template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
		template = cv2.Canny(template, 50, 200)
		(tH, tW) = template.shape[:2]

		pyautogui.screenshot('desktop2.png')
		image = cv2.imread('desktop2.png')
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		found = None
		# loop over the scales of the image
		for scale in np.linspace(0.85, 1.15, 15)[::-1]:
			# resize the image according to the scale, and keep track
			# of the ratio of the resizing
			resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
			r = gray.shape[1] / float(resized.shape[1])
			# if the resized image is smaller than the template, then break
			# from the loop
			if resized.shape[0] < tH or resized.shape[1] < tW:
				break

			# detect edges in the resized, grayscale image and apply template
			# matching to find the template in the image
			edged = cv2.Canny(resized, 50, 200)
			result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF_NORMED)
			(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

			# check to see if the iteration should be visualized
			visualized = False
			if visualized:
				# draw a bounding box around the detected region
				clone = np.dstack([edged, edged, edged])
				cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
					(maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
				cv2.imshow("Visualize", clone)
				cv2.waitKey(0)

			# if we have found a new maximum correlation value, then update
			# the bookkeeping variable
			if found is None or maxVal > found[0]:
				found = (maxVal, maxLoc, r, scale)

		# unpack the bookkeeping variable and compute the (x, y) coordinates
		# of the bounding box based on the resized ratio
		(_, maxLoc, r, scale) = found
		print('Best Scale:', found)
		self.scale = scale
		self.r = r
		# (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
		# (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
		# # draw a bounding box around the detected result and display the image
		# cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
		# cv2.imshow("Image", image)
		# cv2.waitKey(0)

		

	def find_tiles(self):
		"""
		Get initial positions of tiles.
		"""
		pyautogui.screenshot('desktop2.png')
		image = cv2.imread('desktop2.png')
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		# resize the image according to the scale, and keep track
		# of the ratio of the resizing
		resized = imutils.resize(gray, width = int(gray.shape[1] * self.scale))
		
		# detect edges in the resized, grayscale image and apply template
		# matching to find the template in the image
		edged = cv2.Canny(resized, 50, 200)
		
		template = cv2.imread('seed_9x9.png')
		template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
		template = cv2.Canny(template, 50, 200)
		(tH, tW) = template.shape[:2]

		w, h = template.shape[::-1]
		result = cv2.matchTemplate(edged,template,cv2.TM_CCOEFF_NORMED)
		(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

		r = self.r
		(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
		(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
		print(startX, endX, startY, endY)
		# draw a bounding box around the detected result and display the image
		# cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)

		# adjust to crop out shadow border
		adj = int((endX - startX) * 0.035 / 2)
		adj = 0
		print(adj)

		cropped_image = image[(startY+adj):(endY-adj),(startX+adj):(endX-adj)]
		cv2.imshow("Image", cropped_image)
		cv2.waitKey(0)

		# 3.5%

		cv2.imwrite('res.png', image)
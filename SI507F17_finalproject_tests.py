import unittest
from SI507F17_finalproject import *


class VideoTests(unittest.TestCase):
	def setUp(self):
		# archive_url = 'https://www.vox.com/videos/archives/2'
		# archive_html = get_html_from_url(archive_url)
		# archive_soup = Soup(archive_html,'html.parser')
		# test_archive_list = archive_soup.find_all('div',{'class':'c-entry-box--compact'})
		self.archive_data = extract_video_data(video_archive_list)
		self.test_video_objects = []
		for eachlist in self.archive_data:
			self.test_video_objects.append(Video(eachlist))

	def test_video_extraction(self):
		self.assertTrue(type(self.archive_data),type([1,'test',43]))
		self.assertTrue(len(self.archive_data[3]),4)

	def test_video_class(self):
		self.assertTrue(type(self.test_video_objects[0].title),type("string"))
		self.assertTrue(type(self.test_video_objects[1].url), type("string"))
		self.assertTrue(type(self.test_video_objects[2].authors), type([1,'text']))
		self.assertTrue(type(self.test_video_objects[3].date), type("string"))
		self.assertTrue(type(self.test_video_objects[4].__contains__("text")),type(bool))
		self.assertTrue(len(self.test_video_objects[5].get_video_dict()),4)
		self.assertIsInstance(self.test_video_objects[6],Video)

class PodTests(unittest.TestCase):
	def test_pod_extraction(self):
		self.assertTrue(type(p_list),type([4,"test"]))
		self.assertTrue(type(p_list[0]),type([4,"test"]))
		self.assertTrue(len(p_list[1]),3)

	def test_pod_class(self):
		self.assertTrue(type(pod_show_objects[0].showtitle),type("string"))
		self.assertTrue(type(pod_show_objects[1].eptitle),type("string"))
		self.assertTrue(type(pod_show_objects[2].epdate),type("string"))
		self.assertIsInstance(pod_show_objects[3],Podcast)
		self.assertTrue(len(pod_show_objects[4].get_pod_dict()),2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
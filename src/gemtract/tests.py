# This file is part of the GEMtractor
# Copyright (C) 2019 Martin Scharm <https://binfalse.de>
# 
# The GEMtractor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# The GEMtractor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import os
import tempfile
from xml.dom import minidom

from django.test import Client, TestCase
from libsbml import SBMLReader

from modules.gemtractor.utils import Utils

from .forms import ExportForm

# logging.getLogger(__name__).debug("---->>>>> " + str(j))


# Create your tests here.
class GemtractTest(TestCase):
  def setUp(self):
    self.client = Client()
    
  def test_untained_gets (self):
    response = self.client.get('/gemtract/')
    self.assertEqual(response.status_code, 200)
    self.assertTrue (b"Select a model" in response.content)
    
    response = self.client.get('/gemtract/filter')
    self.assertEqual(response.status_code, 302)
    self.assertEqual("/gemtract/", response["location"])
    
    response = self.client.get('/gemtract/export')
    self.assertEqual(response.status_code, 302)
    self.assertEqual("/gemtract/", response["location"])
    
  def test_index_lost_model (self):
    d = tempfile.TemporaryDirectory()
    with self.settings(STORAGE=d.name):
      with open("test/gene-filter-example.xml") as fp:
        response = self.client.post('/gemtract/', {"custom-model": fp})
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/gemtract/filter", response["location"])
        
        # test session uploaded file
    
        response = self.client.get('/api/get_session_data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("success", response.json()["status"], msg = "response was: " + str(response.json()))
        self.assertEqual("yes", response.json()["data"]["session"]["has_session"])
        self.assertEqual(len (response.json()["data"]["files"]), 1)
        
        # make sure model is stored on server
        uploaded_file = Utils.get_upload_path (response.json ()["data"]["session"]["model_id"])
        self.assertTrue(os.path.isfile (uploaded_file))
        
        os.remove (uploaded_file)
        
        
        response = self.client.get('/gemtract/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue (b"Select a model" in response.content)
        # expect an error, as the file is lost...
        self.assertTrue(b"did not find model on the server" in response.content)
    
  def test_filter_lost_model (self):
    d = tempfile.TemporaryDirectory()
    with self.settings(STORAGE=d.name):
      with open("test/gene-filter-example.xml") as fp:
        response = self.client.post('/gemtract/', {"custom-model": fp})
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/gemtract/filter", response["location"])
        
        # test session uploaded file
    
        response = self.client.get('/api/get_session_data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("success", response.json()["status"], msg = "response was: " + str(response.json()))
        self.assertEqual("yes", response.json()["data"]["session"]["has_session"])
        self.assertEqual(len (response.json()["data"]["files"]), 1)
        
        # make sure model is stored on server
        uploaded_file = Utils.get_upload_path (response.json ()["data"]["session"]["model_id"])
        self.assertTrue(os.path.isfile (uploaded_file))
        
        os.remove (uploaded_file)
        
        
        response = self.client.get('/gemtract/filter')
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/gemtract/", response["location"])
    
  def test_export_lost_model (self):
    d = tempfile.TemporaryDirectory()
    with self.settings(STORAGE=d.name):
      with open("test/gene-filter-example.xml") as fp:
        response = self.client.post('/gemtract/', {"custom-model": fp})
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/gemtract/filter", response["location"])
        
        # test session uploaded file
    
        response = self.client.get('/api/get_session_data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("success", response.json()["status"], msg = "response was: " + str(response.json()))
        self.assertEqual("yes", response.json()["data"]["session"]["has_session"])
        self.assertEqual(len (response.json()["data"]["files"]), 1)
        
        # make sure model is stored on server
        uploaded_file = Utils.get_upload_path (response.json ()["data"]["session"]["model_id"])
        self.assertTrue(os.path.isfile (uploaded_file))
        
        os.remove (uploaded_file)
        
        
        response = self.client.get('/gemtract/export')
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/gemtract/", response["location"])
    
    
  def test_workflow_upload (self):
    d = tempfile.TemporaryDirectory()
    with self.settings(STORAGE=d.name):
      with open("test/gene-filter-example.xml") as fp:
        response = self.client.post('/gemtract/', {"custom-model": fp})
        self.assertEqual(response.status_code, 302)
        self.assertEqual("/gemtract/filter", response["location"])
        
        # test session uploaded file
    
        response = self.client.get('/api/get_session_data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("success", response.json()["status"], msg = "response was: " + str(response.json()))
        self.assertEqual("yes", response.json()["data"]["session"]["has_session"])
        self.assertEqual(len (response.json()["data"]["files"]), 1)
        
        
        response = self.client.post('/api/store_filter', json.dumps({'species': ["x","y","a"], 'reaction': ["x","y","a"], 'enzymes': ["x","y","x","y"]}),content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual("success", response.json()["status"], msg = "response was: " + str(response.json()))
        f = response.json()["filter"]
        self.assertEqual(len(f["filter_species"]), 3)
        self.assertEqual(len(f["filter_reactions"]), 3)
        self.assertEqual(len(f["filter_enzymes"]), 4)
        
        
        response = self.client.get('/gemtract/filter')
        self.assertEqual(response.status_code, 200)
        self.assertTrue (b"Trim the Model" in response.content)
        
        
        
        response = self.client.get('/gemtract/export')
        self.assertEqual(response.status_code, 200)
        self.assertTrue (b"Export the Model" in response.content)
        
        
        form = self._create_export ('mn', 'sbml', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        valid, sbml_rn = self._valid_sbml (response.content)
        self.assertTrue (valid, msg="invalid SBML of rn")
        
        rnSpecies = sbml_rn.getModel ().getNumSpecies ()
        rnReactions = sbml_rn.getModel ().getNumReactions ()
        rnEdges = 0
        for r in range (rnReactions):
          reaction = sbml_rn.getModel ().getReaction (r)
          rnEdges += reaction.getNumReactants ()
          rnEdges += reaction.getNumProducts ()
        
        form = self._create_export ('en', 'sbml', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        valid, sbml_en = self._valid_sbml (response.content)
        self.assertTrue (valid, msg="invalid SBML of en")
        
        enSpecies = sbml_en.getModel ().getNumSpecies ()
        enReactions = sbml_en.getModel ().getNumReactions ()
        enEdges = 0
        for r in range (enReactions):
          reaction = sbml_en.getModel ().getReaction (r)
          enEdges += reaction.getNumReactants ()
          enEdges += reaction.getNumProducts ()
        
        
        
        form = self._create_export ('mn', 'graphml', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        self.assertTrue (self._valid_xml (response.content))
        c = response.content.decode("utf-8")
        self.assertEqual (c.count ("<node "), rnSpecies + rnReactions)
        self.assertEqual (c.count (">species</data"), rnSpecies)
        self.assertEqual (c.count (">reaction<"), rnReactions)
        self.assertEqual (c.count ("<edge"), rnEdges)
        
        
        
        form = self._create_export ('en', 'graphml', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        self.assertTrue (self._valid_xml (response.content))
        c = response.content.decode("utf-8")
        self.assertEqual (c.count ("<node "), enSpecies)
        self.assertEqual (c.count (">enzyme</data") + c.count (">enzyme_complex</data"), enSpecies)
        self.assertEqual (c.count ("<edge"), enReactions)
        
        
        
        form = self._create_export ('mn', 'gml', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        c = response.content.decode("utf-8")
        self.assertEqual (c.count ("node ["), rnSpecies + rnReactions)
        self.assertEqual (c.count ("edge ["), rnEdges)
        
        
        
        form = self._create_export ('en', 'gml', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        c = response.content.decode("utf-8")
        self.assertEqual (c.count ("node ["), enSpecies)
        self.assertEqual (c.count ("edge ["), enReactions)
        
        
        
        form = self._create_export ('mn', 'dot', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        c = response.content.decode("utf-8")
        self.assertEqual (c.count ("label="), rnSpecies + rnReactions)
        self.assertEqual (c.count (" -> "), rnEdges)
        
        
        
        form = self._create_export ('en', 'dot', False, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        c = response.content.decode("utf-8")
        self.assertEqual (c.count ("label="), enSpecies)
        self.assertEqual (c.count (" -> "), enReactions)
        
        
        
        
        
        response = self.client.post('/api/store_filter', json.dumps({'species': [], 'reaction': [], 'enzymes': ["b"]}),content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual("success", response.json()["status"], msg = "response was: " + str(response.json()))
        f = response.json()["filter"]
        self.assertEqual(len(f["filter_species"]), 0)
        self.assertEqual(len(f["filter_reactions"]), 0)
        self.assertEqual(len(f["filter_enzymes"]), 1)
        self.assertEqual(len(f["filter_enzyme_complexes"]), 0)
        
        
        response = self.client.get('/gemtract/filter')
        self.assertEqual(response.status_code, 200)
        self.assertTrue (b"Trim the Model" in response.content)
        
        
        
        form = self._create_export ('en', 'dot', False, True, False)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        c = response.content.decode("utf-8")
        self.assertEqual (c.count ("label="), 12)
        self.assertEqual (c.count (" -> "), enReactions)
        
        form = self._create_export ('en', 'dot', False, True, True)
        self.assertTrue (form.is_valid())
        response = self.client.post('/api/export', form.cleaned_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["name"]) > 0)
        self.assertTrue(len(data["mime"]) > 0)
        response = self.client.post('/api/serve/' + data["name"] + "/" + data["mime"])
        c = response.content.decode("utf-8")
        # b, c, and b+c should now be removed:
        self.assertEqual (c.count ("label="), 9)
        
        
        
        
    
  def _create_export (self, network_type, network_format, remove_reaction_enzymes_removed, remove_reaction_missing_species, removing_enzyme_removes_complex = True):
    return ExportForm(data={
      'network_type': network_type,
      'remove_reaction_enzymes_removed': remove_reaction_enzymes_removed,
      'remove_reaction_missing_species': remove_reaction_missing_species,
      'network_format': network_format,
      'removing_enzyme_removes_complex': removing_enzyme_removes_complex
      })
  
  def _valid_xml (self, xml):
    try:
      minidom.parseString (xml)
      return True
    except:
      logging.getLogger(__name__).info("XML BAD")
      return False
  
  def _valid_sbml (self, xml):
    if not self._valid_xml (xml):
      return False, None
    
    sbml = SBMLReader().readSBMLFromString(xml.decode("utf-8"))
    if sbml.getNumErrors() > 0:
      for i in range (0, sbml.getNumErrors()):
        logging.getLogger(__name__).info("SBML BAD: " + sbml.getError(i).getMessage())
      return False, None
    return True, sbml
  
  def test_export_form(self):
    form = self._create_export ('en', 'sbml', False, True)
    self.assertTrue (form.is_valid())
    self.assertTrue (form.cleaned_data['remove_reaction_enzymes_removed'])
    
    form = self._create_export ('blah', 'sbml', False, True)
    self.assertFalse (form.is_valid())
    
    form = self._create_export ('mn', 'gml', False, True)
    self.assertTrue (form.is_valid())
    
    form = self._create_export ('mn', 'gasdfml', False, True)
    self.assertFalse (form.is_valid())

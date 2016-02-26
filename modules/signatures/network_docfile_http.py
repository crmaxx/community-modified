# Copyright (C) 2016 Kevin Ross. Also uses code by Will Metcalf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from lib.cuckoo.common.abstracts import Signature

class NetworkDocumentHTTP(Signature):
    name = "network_document_http"
    description = "A document file initiated network communications indicative of a potential exploit or payload download"
    severity = 3
    confidence = 20
    categories = ["virus", "exploit"]
    authors = ["Kevin Ross", "Will Metcalf"]
    minimum = "1.2"
    evented = True
    match = True

    def __init__(self, *args, **kwargs):
        Signature.__init__(self, *args, **kwargs)
        self.data = []
        self.office_proc_list =["wordview.exe","winword.exe","excel.exe","powerpnt.exe","outlook.exe","acrord32.exe","acrord64.exe"]

    filter_apinames = set(["InternetCrackUrlW","InternetCrackUrlA","URLDownloadToFileW","HttpOpenRequestW","InternetReadFile"])
    filter_analysistypes = set(["file"])

    def on_call(self, call, process):
        pname = process["process_name"].lower()
        if pname in self.office_proc_list:
            addit = None
            if call["api"] == "URLDownloadToFileW":
                buff = self.get_argument(call, "FileName").lower()
                addit = {"http_filename": "%s_URLDownloadToFileW_%s" % (pname,buff)}
            if call["api"] == "HttpOpenRequestW":
                buff = self.get_argument(call, "Path").lower()
                addit = {"http_request_path": "%s_HttpOpenRequestW_%s" % (pname,buff)}
            if call["api"] == "InternetCrackUrlW":
                buff = self.get_argument(call, "Url").lower()
                addit = {"http_request": "%s_InternetCrackUrlW_%s" % (pname,buff)}
            if call["api"] == "InternetCrackUrlA":
                buff = self.get_argument(call, "Url").lower()
                addit = {"http_request": "%s_InternetCrackUrlA_%s" % (pname,buff)}
            if addit and addit not in self.data:
                self.data.append(addit)

        return None

    def on_complete(self):
        if self.data:
            return True

        return False

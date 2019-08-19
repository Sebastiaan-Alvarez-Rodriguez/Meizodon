#!/usr/bin/env python

import re

import lib.analysis.analyse as a
import lib.analysis.component as a_comp
import lib.dynamic.component as comp
import lib.independence.fs as fs
import lib.settings as s
import lib.ui.menu as menu

# The greater purpose of (functions in) this file is to
# ask user what results are to be analysed

class AnalysisMenuHandler(object):
    '''Object to handle sequential submenu calls, 
    and to provide selection filters'''

    # Constructor
    # resultpath is the path where all results are kept
    # components is a list of available methodcomponent
    def __init__(self, resultpath, components):
        self.current_path = resultpath
        self.components = components

    # Returns a list of dirs with datetime name, found in Meizodon/results
    def get_result_dirs(self):
        if not fs.isdir(self.current_path):
            return []
        return_list = fs.lsonlydir(self.current_path, full_paths=True)

        if fs.isdir(s.analyseddir):
            already_analysed = fs.lsonlydir(s.analyseddir)
        else:
            already_analysed = []
        regex = '[0-9]+-[0-9]{2}-[0-9]{2}\([0-9]{2}:[0-9]{2}:[0-9]{2}\)'
        pattern = re.compile(regex)

        for item in return_list:
            basename = fs.basename(item)
            if (not pattern.match(basename)) or (basename in already_analysed):
                return_list.remove(item)
        return return_list

    # Returns a list of dirs in Meizodon/results/<datetime>/,
    # with names corresponding to available methods
    def get_result_sub_dirs(self):
        return_list = fs.lsonlydir(self.current_path)
        component_names = [str(x) for x in self.components]

        for item in return_list:
            if not item in component_names:
                return_list.remove(item)
        return return_list


    # Takes a full path to a result, returns an AnalysisComponent
    # path like: results/<datetime>/DroidSafe/adsvr.soporteweb.es.apk
    def get_analysis_component(self, path):
        path_array = fs.split(path)
        datetime = path_array[-3]
        method_name = path_array[-2]
        apk_name = path_array[-1]

        method = comp.Component.get_component_for_name(self.components, method_name)
        results = fs.join(s.resultsdir,datetime,'results.csv')

        analysis_result_loc = fs.join(s.analyseddir,datetime,method_name,apk_name)
        return a_comp.AnalysisComponent(path, analysis_result_loc, method, results)

    # Takes list of full paths to a result, returns list of AnalysisComponents
    # path like: [results/<datetime>/DroidSafe/adsvr.soporteweb.es.apk, ...]
    def get_analysis_components(self, paths):
        analysiscomponents = []
        for path in paths:
            analysiscomponents.append(self.get_analysis_component(path))
        return analysiscomponents

    # Takes list of paths to methods, returns list of AnalysisComponents
    # path like: [results/<datetime>/DroidSafe, results/<datetime>/JN-SAF]
    def get_sub_all_analysis_components(self, paths):
        analysiscomponents = []
        for path in paths:
            contents = fs.lsonlydir(path, full_paths=True)
            analysiscomponents.extend(self.get_analysis_components(contents))
        return analysiscomponents

    # Takes list of path to execution results, returns list of AnalysisComponents
    # path like: [results/2019-04-14(13:59:55), results/2019-05-24(01:23:34)]
    def get_all_analysis_components(self, paths):
        analysiscomponents = []
        for path in paths:
            contents = fs.lsonlydir(path, full_paths=True)
            analysiscomponents.extend(self.get_sub_all_analysis_components(contents))
        return analysiscomponents


    # Perform analysis on one or more full execution results
    # path like: [results/2019-04-14(13:59:55), results/2019-05-24(01:23:34)]
    def analyse_all(self, paths):
        analysiscomponents = self.get_all_analysis_components(paths)
        a.analyse_all(analysiscomponents)

    # Perform analysis on one or more components from a execution results
    # path like: [results/<datetime>/DroidSafe, results/<datetime>/JN-SAF]
    def analyse_sub_all(self, paths):
        analysiscomponents = self.get_sub_all_analysis_components(paths)
        a.analyse_all(analysiscomponents)

    # Perform analysis on one or more apks from one component from one execution result
    # path like: [results/<datetime>/DroidSafe/adsvr.soporteweb.es.apk, ...]
    def analyse_sub_sub_all(self, paths):
        analysiscomponents = self.get_analysis_components(paths)
        a.analyse_all(analysiscomponents)

    # Perform analysis on exactly 1 apk's execution result for one component
    # path like: results/<datetime>/DroidSafe/adsvr.soporteweb.es.apk
    def analyse_sub_sub_single(self, path):
        analysiscomponent = self.get_analysis_component(path)
        a.analyse_all([analysiscomponent])

    # Shows user a menu to determine which analyse generated 
    # result directories should be analysed
    def analysis_menu(self):
        if not fs.isdir(s.resultsdir) or not fs.ls(s.resultsdir):
            print('Nothing to analyse.')
            return

        while True:
            print('Results for which run do you want to analyse?')
            options = self.get_result_dirs()

            chosenopts, result = menu.standard_menu(options, lambda x: fs.basename(str(x)))
            if result == menu.MenuResults.CHOSEN:
                if len(chosenopts) == 1:
                    self.current_path = fs.join(self.current_path,chosenopts[0])
                    self.analysis_submenu()
                    return
                elif len(chosenopts) > 1:
                    self.analyse_all(chosenopts)
                    return
            elif result == menu.MenuResults.EVERYTHING:
                self.analyse_all(chosenopts)
                return
            elif result == menu.MenuResults.BACK:
                return

    # Shows user a menu to further decide which 
    # execution results should be analysed
    def analysis_submenu(self):
        if not fs.ls(self.current_path):
            print('Nothing to analyse here')
            return

        while True:
            print('Results for which method do you want to analyse?')
            options = self.get_result_sub_dirs()

            chosenopts, result = menu.standard_menu(options, lambda x: str(x))
            if result == menu.MenuResults.CHOSEN:
                if len(chosenopts) == 1:
                    self.current_path = fs.join(self.current_path,chosenopts[0])
                    self.analysis_sub_submenu()
                    return
                elif len(chosenopts) > 1:
                    self.analyse_sub_all([fs.join(self.current_path,x) for x in chosenopts])
                    return
            elif result == menu.MenuResults.EVERYTHING:
                self.analyse_sub_all([fs.join(self.current_path,x) for x in chosenopts])
                return
            elif result == menu.MenuResults.BACK:
                self.current_path = fs.dirname(self.current_path)
                return

    # Shows user a menu to further decide which 
    # execution results should be analysed
    def analysis_sub_submenu(self):
        if not fs.ls(self.current_path):
            print('Nothing to analyse here')
            return

        print('Results for which apk do you want to analyse?')
        options = fs.lsonlydir(self.current_path)

        chosenopts, result = menu.standard_menu(options, lambda x: str(x))
        if result == menu.MenuResults.CHOSEN:
            if len(chosenopts) == 1:
                self.current_path = fs.join(self.current_path,chosenopts[0])
                self.analyse_sub_sub_single(self.current_path)
            elif len(chosenopts) > 1:
                self.analyse_sub_sub_all([fs.join(self.current_path,x) for x in chosenopts])
        elif result == menu.MenuResults.EVERYTHING:
            self.analyse_sub_sub_all([fs.join(self.current_path,x) for x in chosenopts])
        elif result == menu.MenuResults.BACK:
            self.current_path = fs.dirname(self.current_path)

# Returns True if this window should be shown in the main menu
# Otherwise, it returns False
def should_show(components):
    handler = AnalysisMenuHandler(s.resultsdir, components)
    return len(handler.get_result_dirs()) > 0

# Main function of this menu. Creates a handler-object and executes it
def analysis_menu(components):
    handler = AnalysisMenuHandler(s.resultsdir, components)
    handler.analysis_menu()

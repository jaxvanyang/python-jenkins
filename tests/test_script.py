from mock import patch

import jenkins
from jenkins import RUNSCRIPT_MAGIC_STR as MAGIC_STR
from tests.base import JenkinsTestBase


class JenkinsScriptTest(JenkinsTestBase):

    @patch.object(jenkins.Jenkins, 'jenkins_open', return_value='Hello World!\n{}'.format(MAGIC_STR))
    def test_run_script(self, jenkins_mock):
        self.j.run_script(u'println(\"Hello World!\")')

        self.assertEqual(
            jenkins_mock.call_args[0][0].url,
            self.make_url('scriptText'))
        self._check_requests(jenkins_mock.call_args_list)

    @patch.object(jenkins.Jenkins, 'jenkins_open', return_value='\n{}'.format(MAGIC_STR))
    def test_run_script_without_print(self, jenkins_mock):
        self.j.run_script(u'\"Hello World!\"')

        self.assertEqual(
            jenkins_mock.call_args[0][0].url,
            self.make_url('scriptText'))
        self._check_requests(jenkins_mock.call_args_list)

    @patch.object(jenkins.Jenkins, 'jenkins_open', return_value='Hello World!\n{}'.format(MAGIC_STR))
    def test_run_script_node(self, jenkins_mock):
        self.j.run_script(u'println(\"Hello World!\")', node='(master)')

        self.assertEqual(
            jenkins_mock.call_args[0][0].url,
            self.make_url('computer/(master)/scriptText'))
        self._check_requests(jenkins_mock.call_args_list)

    @patch.object(jenkins.Jenkins, 'jenkins_open', return_value='Yes\n{}'.format(MAGIC_STR))
    def test_run_script_urlproof(self, jenkins_mock):
        self.j.run_script(u'if (a == b && c ==d) { println(\"Yes\")}')

        self.assertEqual(
            jenkins_mock.call_args[0][0].url,
            self.make_url('scriptText'))
        self._check_requests(jenkins_mock.call_args_list)

    @patch.object(jenkins.Jenkins, 'jenkins_open', return_value='\n{}'.format(MAGIC_STR))
    def test_install_plugin(self, jenkins_mock):
        '''Installation of plugins is done with the run_script method
        '''
        j = jenkins.Jenkins(self.make_url(''), 'test', 'test')
        j.install_plugin("jabber")
        self.assertEqual(
            jenkins_mock.call_args[0][0].url,
            self.make_url('scriptText'))
        self._check_requests(jenkins_mock.call_args_list)

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    @patch.object(jenkins.Jenkins, 'run_script')
    def test_install_plugin_with_dependencies(self, run_script_mock, jenkins_mock):
        '''Verify install plugins without dependencies
        '''
        j = jenkins.Jenkins(self.make_url(''), 'test', 'test')
        j.install_plugin("jabber")
        self.assertEqual(len(run_script_mock.call_args_list), 2)
        self.assertEqual(run_script_mock.call_args_list[0][0][0],
                         ('Jenkins.instance.updateCenter.getPlugin(\"jabber\")'
                          '.getNeededDependencies().each{it.deploy()};Jenkins'
                          '.instance.updateCenter.getPlugin(\"jabber\").deploy();'))
        self.assertEqual(run_script_mock.call_args_list[1][0][0],
                         ('println(Jenkins.instance.updateCenter'
                          '.isRestartRequiredForCompletion())'))

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    @patch.object(jenkins.Jenkins, 'run_script')
    def test_install_plugin_without_dependencies(self, run_script_mock, jenkins_mock):
        '''Verify install plugins without dependencies
        '''
        j = jenkins.Jenkins(self.make_url(''), 'test', 'test')
        j.install_plugin("jabber", include_dependencies=False)
        self.assertEqual(len(run_script_mock.call_args_list), 2)
        self.assertEqual(run_script_mock.call_args_list[0][0][0],
                         ('Jenkins.instance.updateCenter'
                          '.getPlugin(\"jabber\").deploy();'))
        self.assertEqual(run_script_mock.call_args_list[1][0][0],
                         ('println(Jenkins.instance.updateCenter'
                          '.isRestartRequiredForCompletion())'))

    @patch.object(jenkins.Jenkins, 'jenkins_open', return_value='false\n{}'.format(MAGIC_STR))
    def test_install_plugin_no_restart(self, jenkins_mock):
        '''Verify install plugin does not need a restart
        '''
        j = jenkins.Jenkins(self.make_url(''), 'test', 'test')
        self.assertFalse(j.install_plugin("jabber"))

    @patch.object(jenkins.Jenkins, 'jenkins_open', return_value='true\n{}'.format(MAGIC_STR))
    def test_install_plugin_restart(self, jenkins_mock):
        '''Verify install plugin needs a restart
        '''
        j = jenkins.Jenkins(self.make_url(''), 'test', 'test')
        self.assertTrue(j.install_plugin("jabber"))

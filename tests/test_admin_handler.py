# RandTalkBot Bot matching you with a random person on Telegram.
# Copyright (C) 2016 quasiyoke
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from unittest.mock import create_autospec
import asynctest
from asynctest.mock import call, patch, Mock, CoroutineMock
from randtalkbot.admin_handler import AdminHandler
from randtalkbot.admin_handler import StrangerServiceError
from randtalkbot.stranger_setup_wizard import StrangerSetupWizard


class TestAdminHandler(asynctest.TestCase):
    @patch('randtalkbot.stranger_handler.StrangerService', Mock())
    @patch('randtalkbot.stranger_handler.StrangerSetupWizard', create_autospec(StrangerSetupWizard))
    @patch('randtalkbot.stranger_sender_service.StrangerSenderService._instance')
    def setUp(self, stranger_sender_service):
        from randtalkbot.stranger_handler import StrangerSetupWizard as \
            stranger_setup_wizard_cls_mock
        from randtalkbot.stranger_handler import StrangerService as stranger_service_cls_mock
        self.stranger = CoroutineMock()
        stranger_service = stranger_service_cls_mock.get_instance.return_value
        stranger_service.get_or_create_stranger.return_value = self.stranger
        stranger_setup_wizard_cls_mock.reset_mock()
        self.stranger_setup_wizard_cls_mock = stranger_setup_wizard_cls_mock
        self.stranger_setup_wizard = stranger_setup_wizard_cls_mock.return_value
        self.stranger_setup_wizard.handle = CoroutineMock()
        self.initial_msg = {
            'from': {
                'id': 31416,
                },
            }
        self.sender = stranger_sender_service.get_or_create_stranger_sender.return_value
        self.sender.send_notification = CoroutineMock()
        self.admin_handler = AdminHandler(
            (Mock(), self.initial_msg, 31416),
            event_space=None,
            timeout=1,
            )
        self.stranger_sender_service = stranger_sender_service

    @patch('randtalkbot.admin_handler.StrangerService', Mock())
    async def test_handle_command_clear(self):
        from randtalkbot.admin_handler import StrangerService
        stranger = CoroutineMock()
        stranger_service = StrangerService.get_instance.return_value
        stranger_service.get_stranger.return_value = stranger
        message = Mock()
        message.command_args = '31416'
        await self.admin_handler._handle_command_clear(message)
        stranger_service.get_stranger.assert_called_once_with(31416)
        stranger.end_talk.assert_called_once_with()
        self.sender.send_notification.assert_called_once_with('Stranger {0} was cleared', 31416)

    @patch('randtalkbot.admin_handler.StrangerService', Mock())
    async def test_handle_command_clear__incorrect_telegram_id(self):
        from randtalkbot.admin_handler import StrangerService
        stranger_service = StrangerService.get_instance.return_value
        message = Mock()
        message.command_args = 'foo'
        await self.admin_handler._handle_command_clear(message)
        stranger_service.get_stranger.assert_not_called()
        self.assertEqual(
            self.sender.send_notification.call_args_list,
            [
                call('Is it really telegram_id: \"{0}\"?', 'foo'),
                call('Use it this way: `/clear 31416 27183`'),
                ],
            )

    @patch('randtalkbot.admin_handler.StrangerService', Mock())
    async def test_handle_command_clear__unknown_stranger(self):
        from randtalkbot.admin_handler import StrangerService
        error = StrangerServiceError()
        stranger_service = StrangerService.get_instance.return_value
        stranger_service.get_stranger.side_effect = error
        message = Mock()
        message.command_args = '31416'
        await self.admin_handler._handle_command_clear(message)
        stranger_service.get_stranger.assert_called_once_with(31416)
        self.assertEqual(
            self.sender.send_notification.call_args_list,
            [
                call('Stranger {0} wasn\'t found: {1}', 31416, error),
                call('Use it this way: `/clear 31416 27183`'),
                ],
            )

    @patch('randtalkbot.admin_handler.StrangerService', Mock())
    async def test_handle_command_pay(self):
        from randtalkbot.admin_handler import StrangerService
        stranger_service = StrangerService.get_instance.return_value
        stranger = CoroutineMock()
        stranger_service.get_stranger.return_value = stranger
        message = Mock()
        message.command_args = '31416 27183 foo gratitude'
        await self.admin_handler._handle_command_pay(message)
        stranger_service.get_stranger.assert_called_once_with(31416)
        stranger.pay.assert_called_once_with(27183, 'foo gratitude')
        self.sender.send_notification.assert_called_once_with('Success.')

    @patch('randtalkbot.admin_handler.StrangerService', Mock())
    async def test_handle_command_pay__incorrect_telegram_id(self):
        from randtalkbot.admin_handler import StrangerService
        stranger_service = StrangerService.get_instance.return_value
        message = Mock()
        message.command_args = 'foo'
        await self.admin_handler._handle_command_pay(message)
        stranger_service.get_stranger.assert_not_called()
        self.sender.send_notification.assert_called_once_with(
            'Please specify Telegram ID and bonus amount like this: `/pay 31416 10 Thanks!`',
            )

    @patch('randtalkbot.admin_handler.StrangerService', Mock())
    async def test_handle_command_pay__no_command_args(self):
        from randtalkbot.admin_handler import StrangerService
        stranger_service = StrangerService.get_instance.return_value
        message = Mock()
        message.command_args = None
        await self.admin_handler._handle_command_pay(message)
        stranger_service.get_stranger.assert_not_called()
        self.sender.send_notification.assert_called_once_with(
            'Please specify Telegram ID and bonus amount like this: `/pay 31416 10 Thanks!`',
            )

    @patch('randtalkbot.admin_handler.StrangerService', Mock())
    async def test_handle_command_pay__unknown_stranger(self):
        from randtalkbot.admin_handler import StrangerService
        stranger_service = StrangerService.get_instance.return_value
        error = StrangerServiceError()
        stranger_service.get_stranger.side_effect = error
        message = Mock()
        message.command_args = '31416 27183'
        await self.admin_handler._handle_command_pay(message)
        stranger_service.get_stranger.assert_called_once_with(31416)
        self.sender.send_notification.assert_called_once_with(
            'Stranger wasn\'t found: {0}',
            error,
            )

    @patch('randtalkbot.admin_handler.StrangerHandler.handle_command')
    async def test_handle_command__other_command(self, handle_command):
        message = Mock()
        message.command = 'foo_command'
        message.command_args = 'foo_args'
        await self.admin_handler.handle_command(message)
        handle_command.assert_called_once_with(message)

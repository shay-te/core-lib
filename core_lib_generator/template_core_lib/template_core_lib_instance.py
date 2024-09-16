from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
# template_core_lib_import


class TemplateCoreLibInstance(object):
    _app_instance = None

    @staticmethod
    def init(core_lib_cfg):
        if not TemplateCoreLibInstance._app_instance:
            # WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK) #TODO: initilazie the correct server type
            TemplateCoreLibInstance._app_instance = TemplateCoreLibClass(core_lib_cfg)

    @staticmethod
    def get() -> TemplateCoreLibClass:
        return TemplateCoreLibInstance._app_instance
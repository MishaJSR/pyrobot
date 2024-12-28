from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_ID: str
    API_HASH: str
    BOT_NAME: str
    PWD: str

    def get_id(self):
        return self.API_ID

    def get_hash(self):
        return self.API_HASH

    def get_bot_name(self):
        return self.BOT_NAME

    def get_pwd(self):
        return self.PWD



base_settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

import asyncio
import os
from typing import Annotated

from pydantic import SecretStr, conint, BaseModel, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from html_page_generator import AsyncDeepseekClient, AsyncUnsplashClient

from html_page_generator import AsyncPageGenerator

DEBUG_MODE = os.getenv("DEBUG_MODE", False)


async def main():
    async with (
        AsyncUnsplashClient.setup("UNSPLASH_CLIENT_ID", timeout=3),
        AsyncDeepseekClient.setup("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL")
    ):
        async def generate_page(user_prompt: str):
            generator = AsyncPageGenerator(debug_mode=DEBUG_MODE)
            title_saved = False
            async for chunk in generator(user_prompt):
                if title_saved:
                    continue
                if title := generator.html_page.title:
                    print(title)
                    title_saved = True
                print(chunk, end="", flush=True)

            with open(generator.html_page.title + '.html', 'w') as f:
                f.write(generator.html_page.html_code)

            print('Файл успешно сохранён!')


        await generate_page("сайт про динозавров")

if __name__ == "__main__":
    class AppSettings(BaseSettings):
        """Главные настройки приложения. Загружаются из .env."""
        debug: bool = False
        deep_seek_api_key: SecretStr
        unsplash_client_id: SecretStr
        deep_seek_max_connections: Annotated[conint(gt=0), "Максимальное количество подключений"] | None = None
        unsplash_max_connections: Annotated[conint(gt=0), "Максимальное количество подключений"] | None = None
        timeout: Annotated[conint(gt=0), "Таймаут"] | None = None
        deepseek_base_url: AnyHttpUrl
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
        )

    class HtmlPage(BaseModel):
        html_code: str = ""
        title: str = ""

    settings = AppSettings()

    settings_json_format = settings.model_dump_json(indent=4)
    print(settings_json_format)

    asyncio.run(main())


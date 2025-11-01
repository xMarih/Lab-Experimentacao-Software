import { NestFactory } from '@nestjs/core';
import { AppModule } from '../app.module';
import { NewsService } from '../news/news.service';

async function bootstrap() {
  const app = await NestFactory.createApplicationContext(AppModule, {
    logger: ['error', 'warn', 'log'],
  });
  
  try {
    const newsService = app.get(NewsService);
    const rankThreshold = 1;
    const newsCountPerGame = 10000;

    console.log('Starting news synchronization...');
    await newsService.syncNewsForTopGames(rankThreshold, newsCountPerGame);
    console.log('News synchronization completed!');
  } catch (error) {
    console.error('Error during news synchronization:', error);
  } finally {
    await app.close();
    process.exit(0);
  }
}

bootstrap();
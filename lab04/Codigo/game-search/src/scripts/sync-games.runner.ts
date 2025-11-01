import { NestFactory } from '@nestjs/core';
import { AppModule } from '../app.module';
import { GamesService } from '../games/games.service';

async function bootstrap() {
  const app = await NestFactory.createApplicationContext(AppModule, {
    logger: ['error', 'warn', 'log'],
  });
  
  try {
    const gamesService = app.get(GamesService);
    console.log('Starting synchronization...');
    await gamesService.syncTop100Games();
    console.log('Synchronization completed!');
  } catch (error) {
    console.error('Error during synchronization:', error);
  } finally {
    await app.close();
    process.exit(0);
  }
}

bootstrap();
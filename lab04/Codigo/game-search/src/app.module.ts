import { Module } from '@nestjs/common';
import { MongoDatabaseModule } from './database/mongo-database.module';
import { GamesModule } from './games/games.module';
import { NewsModule } from './news/news.module';

@Module({
  imports: [
    MongoDatabaseModule,
    GamesModule,
    NewsModule
  ],
})
export class AppModule {}
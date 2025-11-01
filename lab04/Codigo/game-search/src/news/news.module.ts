// news/news.module.ts
import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { GamesModule } from '../games/games.module';
import { HttpModule } from '@nestjs/axios';
import { News, NewsSchema } from './schema/new.schema';
import { NewsService } from './news.service';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: News.name, schema: NewsSchema }], 'games'),
    HttpModule,
    GamesModule,
  ],
  providers: [NewsService],
  exports: [NewsService],
})
export class NewsModule {}
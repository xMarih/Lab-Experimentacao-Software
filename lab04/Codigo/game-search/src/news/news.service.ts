// news/news.service.ts
import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { GamesService } from '../games/games.service';
import { News } from './schema/new.schema';

@Injectable()
export class NewsService {
  private readonly steamApiKey = '1DF82B1467E5AC639BBD56B8C2249DF6';
  private readonly steamApiBaseUrl = 'https://api.steampowered.com';

  constructor(
    @InjectModel(News.name, 'games') private newsModel: Model<News>,
    private readonly httpService: HttpService,
    private readonly gamesService: GamesService,
  ) {}

  async syncNewsForTopGames(rankThreshold: number, newsCount: number): Promise<void> {
    const games = await this.gamesService.getGamesAboveRank(rankThreshold);
    
    for (const game of games) {
      await this.syncGameNews(game.appid, newsCount);
    }
  }

  async syncGameNews(appid: number, count: number): Promise<void> {
    try {
      const newsItems = await this.fetchGameNews(appid, count);
      await this.saveNews(appid, newsItems);
      await this.gamesService.updateNewsCount(appid, newsItems.length);
    } catch (error) {
      console.error(`Error syncing news for app ${appid}:`, error);
    }
  }

  private async fetchGameNews(appid: number, count: number): Promise<News[]> {
    const url = `${this.steamApiBaseUrl}/ISteamNews/GetNewsForApp/v2/`;
    const response = await firstValueFrom(
      this.httpService.get(url, { params: { key: this.steamApiKey, appid, count } })
    );

    return response.data.appnews.newsitems.map(item => ({
      gid: item.gid,
      title: item.title,
      contents: item.contents,
      date: item.date,
      appid: item.appid,
    }));
  }

  private async saveNews(appid: number, newsItems: News[]): Promise<void> {
    await this.newsModel.deleteMany({ appid });
    if (newsItems.length > 0) {
      await this.newsModel.insertMany(newsItems);
    }
  }
}
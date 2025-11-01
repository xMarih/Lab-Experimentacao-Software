import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { firstValueFrom } from 'rxjs';
import { Game } from './schema/game.schema';

@Injectable()
export class GamesService {
  private readonly steamApiKey = '1DF82B1467E5AC639BBD56B8C2249DF6';
  private readonly steamApiBaseUrl = 'https://api.steampowered.com';

  constructor(
    @InjectModel(Game.name, 'games') private gameModel: Model<Game>,
    private readonly httpService: HttpService,
  ) {}

  async syncTop100Games(): Promise<void> {
    const top100Games = await this.getTop100GamesByConcurrentPlayers();

    const completeGamesData = await this.getCompleteGameDetails(top100Games);
    
    await this.saveGamesToDatabase(completeGamesData);
  }

  private async getTop100GamesByConcurrentPlayers(): Promise<any[]> {
    const url = `${this.steamApiBaseUrl}/ISteamChartsService/GetGamesByConcurrentPlayers/v1/`;
    const params = {
      key: this.steamApiKey,
      input_json: JSON.stringify({
        data_request: {
          include_release: true,
          include_reviews: true,
          include_full_description: true,
        },
      }),
    };

    const response = await firstValueFrom(
      this.httpService.get(url, { params }),
    );

    return response.data.response.ranks.map((game) => ({
      appid: game.appid,
      concurrent_in_game: game.concurrent_in_game,
      peak_in_game: game.peak_in_game,
			rank: game.rank
    }));
  }

  private async getCompleteGameDetails(games: any[]): Promise<any[]> {
    const allApps = await this.getAllSteamApps();
    
    return games.map((game) => {
      const appInfo = allApps.find((app) => app.appid === game.appid);
      return {
        appid: game.appid,
        name: appInfo?.name || `Unknown Game (${game.appid})`,
        concurrent_in_game: game.concurrent_in_game,
        peak_in_game: game.peak_in_game,
				rank: game.rank,
				last_modified: appInfo?.last_modified || null,
        news_count: 0,
      };
    });
  }

  private async getAllSteamApps(): Promise<any[]> {
    const url = `${this.steamApiBaseUrl}/IStoreService/GetAppList/v1/`;
    const params = { key: this.steamApiKey };

    const response = await firstValueFrom(
      this.httpService.get(url, { params }),
    );

    return response.data.response.apps;
  }

  private async saveGamesToDatabase(games: any[]): Promise<void> {
    await this.gameModel.deleteMany({});
    await this.gameModel.insertMany(games);
    
    console.log(`Successfully saved ${games.length} games to database`);
  }

  async getGamesAboveRank(rankThreshold: number): Promise<Game[]> {
    return this.gameModel.find({ rank: { $lte: rankThreshold } }).exec();
  }

  async updateNewsCount(appid: number, count: number): Promise<void> {
    await this.gameModel.updateOne(
      { appid },
      { $set: { news_count: count } }
    ).exec();
  }
}
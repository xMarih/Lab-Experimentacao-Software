import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { GamesService } from './games.service';
import { HttpModule } from '@nestjs/axios';
import { Game, GameSchema } from './schema/game.schema';

@Module({
  imports: [
    HttpModule,
    MongooseModule.forFeature([{ name: Game.name, schema: GameSchema }], 'games'),
  ],
  providers: [GamesService],
  exports: [GamesService],
})
export class GamesModule {}
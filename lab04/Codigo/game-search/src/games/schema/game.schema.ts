import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

@Schema({ timestamps: true })
export class Game extends Document {
  @Prop({ required: true })
  appid: number;

  @Prop()
  name: string;

  @Prop()
  concurrent_in_game: number;

  @Prop()
  peak_in_game: number;

  @Prop()
  last_modified: number;

  @Prop()
  rank: number;

  @Prop()
  news_count: number;
}

export const GameSchema = SchemaFactory.createForClass(Game);
import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

@Schema({ timestamps: true })
export class News extends Document {
  @Prop()
  gid: string;

  @Prop()
  title: string;

  @Prop()
  contents: string;

  @Prop()
  date: number;

  @Prop()
  appid: number;
}

export const NewsSchema = SchemaFactory.createForClass(News);
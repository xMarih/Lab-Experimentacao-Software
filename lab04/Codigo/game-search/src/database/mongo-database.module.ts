import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';

@Module({
  imports: [
    MongooseModule.forRoot('mongodb://admin:password@localhost:27018/games?authSource=admin', {
      connectionName: 'games',
    }),
  ],
  exports: [MongooseModule],
})
export class MongoDatabaseModule {}
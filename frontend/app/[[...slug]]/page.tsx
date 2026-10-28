import Application from '@/components/application';
import {notFound} from 'next/navigation';
const pages=new Set(['','login','register','onboarding','dashboard','household','household/members','meters','readings','bills','statistics','notifications','assistant','settings','admin','admin/users','admin/tariffs','admin/audit','admin/knowledge']);
export default async function Page({params}:{params:Promise<{slug?:string[]}>}){
  const path=(await params).slug?.join('/')||'';
  if(!pages.has(path)&&!/^bills\/[0-9a-f-]{36}$/.test(path))notFound();
  return <Application/>;
}
